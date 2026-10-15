from __future__ import annotations

import re

import yaml
from jinja2 import Environment, FileSystemLoader
from markdown import Extension
from markdown.preprocessors import Preprocessor

from extensions.md_jinja_extensions import register_md_globals

FIGURE_IMPORT = '{% from "figure.html" import figure with context %}\n'

FIGURE_CARD = """
<figure class="figure" style="width: {{ width }}%">
  <img src="{{ path | bust_file_cache | relative_url }}"{% if title %} alt="{{ title }}" title="{{ title }}"{% endif %}{% if zoomable %} data-zoomable{% endif %} loading="lazy">
  {%- if caption %}
  <figcaption>{{ caption }}</figcaption>
  {%- endif %}
</figure>
"""


def fenced(name, body):
    return re.compile(
        rf"^!{name}![ ]*\n(?P<{body}>.*?)(?<=\n)!{name}![ ]*$",
        re.MULTILINE | re.DOTALL,
    )


class TemplateBlockExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {"filters": [{}, "Jinja filters available inside Markdown templates."]}
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.preprocessors.register(TemplateBlockPreprocessor(md, self.getConfigs()), "template_block", 175)
        md.preprocessors.register(MathBlockPreprocessor(md), "math_block", 15)


class TemplateBlockPreprocessor(Preprocessor):
    TEMPLATE_BLOCK = fenced("TEMPLATE", "template")
    FIGURE_CARD_BLOCK = fenced("FIGURECARD", "params")
    JINJA_BLOCK = re.compile(r"\{\{.*?\}\}", re.DOTALL)

    def __init__(self, md, config):
        super().__init__(md)
        self.env = Environment(loader=FileSystemLoader("theme/templates/_includes/"))
        self.env.filters.update(config.get("filters") or {})
        register_md_globals(self.env)
        self.figure_card = self.env.from_string(FIGURE_CARD)

    def render_figure_card(self, params):
        if "path" not in params:
            raise ValueError("Missing required key 'path'.")
        col = int(params.get("col", 8))
        if not 1 <= col <= 12:
            raise ValueError("'col' must be between 1 and 12.")
        return self.figure_card.render(
            path=params["path"],
            title=params.get("title", ""),
            caption=params.get("caption", ""),
            zoomable=bool(params.get("zoomable", True)),
            width=round(100 * col / 12, 2),
        )

    def render_template(self, source):
        if "figure(" in source:
            source = FIGURE_IMPORT + source
        return self.env.from_string(source).render().strip()

    def replace_blocks(self, text, pattern, render, label):
        while match := pattern.search(text):
            try:
                rendered = render(match)
            except Exception as error:
                rendered = f"<p>{label} ERROR: {error}</p>"
            text = f"{text[:match.start()]}\n{rendered}\n{text[match.end():]}"
        return text

    def run(self, lines):
        text = "\n".join(lines)

        def figure_card(match):
            params = yaml.safe_load(match.group("params")) or {}
            if not isinstance(params, dict):
                raise ValueError("FIGURECARD content must be a YAML dictionary.")
            return self.render_figure_card(params)

        text = self.replace_blocks(text, self.FIGURE_CARD_BLOCK, figure_card, "FIGURECARD")
        text = self.replace_blocks(
            text, self.TEMPLATE_BLOCK, lambda m: self.render_template(m.group("template")), "JINJA TEMPLATE"
        )

        start = 0
        while match := self.JINJA_BLOCK.search(text, start):
            try:
                rendered = self.render_template(match.group(0))
            except Exception as error:
                rendered = f"<p>JINJA TEMPLATE ERROR: {error}</p>"
            text = f"{text[:match.start()]}{rendered}{text[match.end():]}"
            start = match.start() + len(rendered)

        return text.split("\n")


class MathBlockPreprocessor(Preprocessor):
    DISPLAY_MATH = re.compile(r"\$\$(?P<math>.*?)\$\$", re.DOTALL)
    INLINE_MATH = re.compile(r"\$(?P<math>[^\$].*?)\$", re.DOTALL)

    def stash(self, pattern, text, opening, closing):
        while match := pattern.search(text):
            placeholder = self.md.htmlStash.store(opening + match.group("math") + closing)
            text = f"{text[:match.start()]}{placeholder}{text[match.end():]}"
        return text

    def run(self, lines):
        text = "\n".join(lines)
        text = self.stash(self.DISPLAY_MATH, text, r"\[", r"\]")
        text = self.stash(self.INLINE_MATH, text, r"\(", r"\)")
        return text.split("\n")
