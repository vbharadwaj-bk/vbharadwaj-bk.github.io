from __future__ import annotations

import copy
import logging
import os
import re
from typing import Any, Dict, List, Optional

import typst
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pelican import signals
from pelican.generators import Generator

log = logging.getLogger(__name__)

MONTH_ABBREVIATIONS = {
    "january": "Jan",
    "february": "Feb",
    "march": "Mar",
    "april": "Apr",
    "may": "May",
    "june": "Jun",
    "july": "Jul",
    "august": "Aug",
    "september": "Sep",
    "october": "Oct",
    "november": "Nov",
    "december": "Dec",
}


def _format_person_name(person: Dict[str, str]) -> str:
    first = (person.get("first") or "").replace("*", "").strip()
    last = (person.get("last") or "").replace("*", "").strip()
    initials = "".join(f"{part[0]}." for part in first.split() if part)
    if initials and last:
        return f"{initials} {last}"
    return initials or last


def _build_typst_publications(
    publications: Optional[List[Dict[str, Any]]],
) -> Dict[str, Any]:
    conference_papers: List[Dict[str, Any]] = []
    journal_papers: List[Dict[str, Any]] = []

    for publication in publications or []:
        if publication.get("type") not in {"inproceedings", "article"}:
            continue

        authors: List[str] = []
        equal_contribution_authors: List[str] = []
        for author in publication.get("author_array", []) or []:
            formatted = _format_person_name(author)
            authors.append(formatted)
            if "*" in (author.get("first") or "") or "*" in (author.get("last") or ""):
                equal_contribution_authors.append(formatted)

        entry = {
            "authors": authors,
            "equal_contribution_authors": equal_contribution_authors,
            "title": publication.get("title"),
            "venue": publication.get("booktitle") or publication.get("journal"),
            "date": _format_badge_year(
                f"{publication.get('month', '')} {publication.get('year', '')}".strip(),
                max_length=100,
            ),
        }

        if publication.get("type") == "inproceedings":
            conference_papers.append(entry)
        else:
            journal_papers.append(entry)

    return {
        "equal_contribution_note": "* denotes equal contribution.",
        "conference_papers": conference_papers,
        "journal_papers": journal_papers,
    }


def _format_badge_year(value: Optional[object], max_length: int = 20) -> Optional[str]:
    if value is None:
        return None
    value = str(value).strip()
    
    value = value.replace("Present", "Now")
    
    for month, abbreviation in MONTH_ABBREVIATIONS.items():
        value = re.sub(rf"\b{month}\b", abbreviation, value, flags=re.IGNORECASE)

    if len(value) <= max_length:
        return value

    value = re.sub(r"\b20(\d{2})\b", r"'\1", value)

    if value.startswith("Summers"):
        if "," in value:
            parts = value.split(",", 1)
            return f"{parts[0]}<br>{parts[1].strip()}"

    if "," in value:
        segments = [segment.strip() for segment in value.split(",") if segment.strip()]
        formatted_segments: List[str] = []
        for segment in segments:
            if len(segment) > max_length:
                for dash in ("–", "—", "-"):
                    if dash in segment:
                        start, end = segment.split(dash, 1)
                        formatted_segments.extend([start.strip(), dash, end.strip()])
                        break
                else:
                    formatted_segments.append(segment)
            else:
                formatted_segments.append(segment)
        return "<br>".join(formatted_segments)

    for dash in ("–", "—", "-"):
        if dash in value:
            start, end = value.split(dash, 1)
            return f"{start.strip()}<br>{dash}<br>{end.strip()}"

    return value


class CVTypstGenerator(Generator):
    def generate_context(self) -> None:
        pass

    def generate_output(self, writer) -> None:
        template_path = self._get_template_path()
        output_path = self._get_output_path()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        cv_page = next(page for page in self.context["pages"] if "cv" in page.metadata)
        cv_data = self._normalize_cv_data(copy.deepcopy(cv_page.metadata["cv"]))
        site = self.context.get("SITE", {})
        cv_data["publications"] = _build_typst_publications(site.get("publications"))

        template_dir = os.path.dirname(template_path) or "."
        template_name = os.path.basename(template_path)
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=StrictUndefined,
        )
        template = env.get_template(template_name)
        rendered = template.render(cv=cv_data)

        typst.compile(rendered.encode("utf-8"), output=output_path)

        log.info("Rendered CV PDF to %s", output_path)

    def _get_template_path(self) -> str:
        return self.settings.get("CV_TEMPLATE_PATH", os.path.join("cv_template", "cv.typst"))

    def _get_output_path(self) -> str:
        output_root = self.settings.get("OUTPUT_PATH", "output")
        relative_output = self.settings.get("CV_PDF_OUTPUT", "cv.pdf")
        return os.path.join(output_root, relative_output)

    def _normalize_cv_data(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        cv_data = dict(cv_data or {})
        name = cv_data.get("name", "")
        parts = name.split()
        if len(parts) >= 2:
            cv_data["short_name"] = f"{parts[0][0]}. {parts[-1]}"
        else:
            cv_data["short_name"] = name

        links = dict(cv_data.get("links") or {})
        if links.get("github") and not links.get("github_handle"):
            links["github_handle"] = links["github"].rstrip("/").split("/")[-1]
        if links.get("orcid") and not links.get("orcid_id"):
            links["orcid_id"] = links["orcid"].rstrip("/").split("/")[-1]
        cv_data["links"] = links

        for entry in cv_data.get("education", []):
            dates = entry.get("dates")
            entry["dates_display"] = dates.replace("-", " --- ") if dates else ""
            advisors = entry.get("advisors") or []
            if isinstance(advisors, list):
                if len(advisors) == 2:
                    entry["advisors_display"] = " and ".join(advisors)
                else:
                    entry["advisors_display"] = ", ".join(advisors)
            else:
                entry["advisors_display"] = str(advisors)

        return cv_data


def get_generators(_pelican_object):
    return CVTypstGenerator


def register():
    signals.get_generators.connect(get_generators)
