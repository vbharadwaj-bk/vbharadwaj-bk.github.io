from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional

import typst
import yaml
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
    "september": "Sept",
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
    for month, abbreviation in MONTH_ABBREVIATIONS.items():
        value = re.sub(rf"\b{month}\b", abbreviation, value, flags=re.IGNORECASE)

    if len(value) <= max_length:
        return value

    value = re.sub(r"\b20(\d{2})\b", r"'\1", value)

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


def build_al_folio_cv_data(
    cv_data: Dict[str, Any], publications: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    sections: List[Dict[str, Any]] = []
    cv_data = cv_data or {}

    def join_list(values: Optional[List[str]]) -> str:
        return ", ".join(values or [])

    general_contents: List[Dict[str, Any]] = []
    if cv_data.get("name"):
        general_contents.append({"name": "Name", "value": cv_data["name"]})

    title = cv_data.get("title")
    if title:
        affiliation = title.replace("Apple Platform Architecture", "Apple")
        general_contents.append({"name": "Affiliation", "value": affiliation})

    skills = cv_data.get("research_interests_and_skills") or {}
    if skills.get("interests"):
        general_contents.append(
            {"name": "Research Interests", "value": join_list(skills.get("interests"))}
        )
    if skills.get("languages"):
        general_contents.append(
            {"name": "Languages", "value": join_list(skills.get("languages"))}
        )

    tools: List[str] = []
    tools.extend(skills.get("parallel_computing") or [])
    tools.extend(skills.get("libraries_and_frameworks") or [])
    if tools:
        general_contents.append({"name": "Tools", "value": join_list(tools)})

    if general_contents:
        sections.append(
            {"title": "General Information", "type": "map", "contents": general_contents}
        )

    education_contents: List[Dict[str, Any]] = []
    for edu in cv_data.get("education", []) or []:
        description: List[str] = []
        advisors = edu.get("advisors") or []
        if advisors:
            advisors_text = (
                " and ".join(advisors) if len(advisors) == 2 else ", ".join(advisors)
            )
            description.append(f"Advisors: {advisors_text}")
        if edu.get("funding"):
            description.append(f"Funding: {edu['funding']}")
        if edu.get("gpa"):
            description.append(f"Cumulative GPA: {edu['gpa']}")

        degree = edu.get("degree") or ""

        education_contents.append(
            {
                "title": degree or None,
                "institution": edu.get("institution"),
                "year": _format_badge_year(edu.get("dates")),
                "description": description or None,
            }
        )

    if education_contents:
        sections.append(
            {"title": "Education", "type": "time_table", "contents": education_contents}
        )

    experience_contents: List[Dict[str, Any]] = []
    for job in cv_data.get("experience", []) or []:
        experience_contents.append(
            {
                "title": job.get("role"),
                "institution": job.get("organization"),
                "year": _format_badge_year(job.get("dates")),
                "description": job.get("highlights"),
            }
        )

    if experience_contents:
        sections.append(
            {
                "title": "Experience",
                "type": "time_table",
                "contents": experience_contents,
            }
        )

    publications = publications or []
    conference_count = len(
        [publication for publication in publications if publication.get("type") == "inproceedings"]
    )
    journal_count = len(
        [publication for publication in publications if publication.get("type") == "article"]
    )
    talks_count = len(cv_data.get("selected_talks") or [])
    teaching_count = len(cv_data.get("teaching") or [])
    summary_parts: List[str] = []
    if conference_count or journal_count:
        if conference_count and journal_count:
            summary_parts.append(
                f"Publications ({conference_count} conference, {journal_count} journal)"
            )
        elif conference_count:
            summary_parts.append(f"Publications ({conference_count} conference)")
        else:
            summary_parts.append(f"Publications ({journal_count} journal)")
    if talks_count:
        summary_parts.append(f"Talks ({talks_count})")
    if teaching_count:
        summary_parts.append(f"Teaching ({teaching_count})")

    summary = "See links in the navigation bar."
    if summary_parts:
        summary = f"{', '.join(summary_parts)}. See links in the navigation bar."

    sections.append(
        {
            "title": "Publications, Talks, and Teaching",
            "type": "list",
            "contents": [summary],
        }
    )

    awards_by_year: List[Dict[str, Any]] = []
    for award in cv_data.get("awards", []) or []:
        year = _format_badge_year(award.get("year"))
        entry = next((item for item in awards_by_year if item["year"] == year), None)
        if entry is None:
            entry = {"year": year, "elements": []}
            awards_by_year.append(entry)
        entry["elements"].append(award.get("name"))

    if awards_by_year:
        sections.append(
            {
                "title": "Awards and Fellowships",
                "type": "time_table",
                "contents": awards_by_year,
            }
        )

    service = cv_data.get("professional_service") or {}
    service_contents: List[Dict[str, Any]] = []
    peer_review = service.get("peer_review") or []
    if peer_review:
        elements = [f"{item.get('year')}: {item.get('venue')}" for item in peer_review]
        service_contents.append(
            {
                "year": "Ongoing",
                "maindescription": "Peer review for the following journals / conferences:",
                "elements": elements,
            }
        )

    for role in service.get("roles", []) or []:
        year = _format_badge_year(role.get("date") or role.get("dates") or role.get("year"))
        entry: Dict[str, Any] = {"year": year}
        if role.get("description"):
            entry["maindescription"] = role.get("title")
            entry["elements"] = [role.get("description")]
        else:
            entry["elements"] = [role.get("title")]
        service_contents.append(entry)

    if service_contents:
        sections.append(
            {
                "title": "Professional Service",
                "type": "time_table",
                "contents": service_contents,
            }
        )

    volunteering_contents: List[Dict[str, Any]] = []
    for volunteer in cv_data.get("volunteering", []) or []:
        if volunteer.get("details"):
            volunteering_contents.append(
                {
                    "year": "Ongoing",
                    "maindescription": volunteer.get("role"),
                    "elements": volunteer.get("details"),
                }
            )
            continue

        entry: Dict[str, Any] = {"year": _format_badge_year(volunteer.get("dates"))}
        if volunteer.get("description"):
            entry["maindescription"] = volunteer.get("role")
            entry["elements"] = [volunteer.get("description")]
        else:
            entry["elements"] = [volunteer.get("role")]
        volunteering_contents.append(entry)

    if volunteering_contents:
        sections.append(
            {
                "title": "Volunteering",
                "type": "time_table",
                "contents": volunteering_contents,
            }
        )

    return sections

class CVTypstGenerator(Generator):
    def generate_context(self) -> None:
        pass

    def generate_output(self, writer) -> None:
        cv_data_path = self._get_cv_data_path()
        template_path = self._get_template_path()
        output_path = self._get_output_path()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(cv_data_path, "rb") as handle:
            cv_data = yaml.safe_load(handle)

        cv_data = self._normalize_cv_data(cv_data)
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

    def _get_cv_data_path(self) -> str:
        content_root = self.settings.get("PATH", "content")
        return self.settings.get("CV_DATA_PATH", os.path.join(content_root, "cv.yaml"))

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
