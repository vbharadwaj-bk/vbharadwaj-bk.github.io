from __future__ import annotations

import logging
import os
from typing import Any, Dict

import typst
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pelican import signals
from pelican.generators import Generator

log = logging.getLogger(__name__)


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
        relative_output = self.settings.get("CV_PDF_OUTPUT", os.path.join("cv", "cv.pdf"))
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
