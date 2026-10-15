import logging

import yaml
from markdown import Markdown
from pelican import signals
from pelican.contents import Content
from pelican.generators import PagesGenerator

log = logging.getLogger(__name__)


class Snippet(Content):
    mandatory_properties = ()
    default_template = None


def render_markdown(generator, markdown, text, source_path, inline=False):
    html = Snippet(
        content=markdown.reset().convert(text),
        metadata=None,
        settings=generator.settings,
        source_path=source_path,
        context=generator.context,
    ).content
    return html.replace("<p>", "").replace("</p>", "") if inline else html


def load_page_list(generator, markdown, source, key, fields):
    page = generator.context["generated_content"].get(source)
    if page is None or key not in page.metadata:
        return []
    items = page.metadata[key]
    for item in items:
        for field, inline in fields:
            item[field] = render_markdown(generator, markdown, item[field], page.source_path, inline)
    return items


def load_latex_macros(content):
    if "latex_macro_file" not in content.metadata:
        return
    with open(content.metadata["latex_macro_file"]) as stream:
        macros = yaml.safe_load(stream)
    macros.update(content.metadata.get("latex_macros") or {})
    content.latex_macros = macros
    content.metadata["latex_macros"] = macros


def process(generators):
    generator = next(g for g in generators if isinstance(g, PagesGenerator))
    markdown = Markdown(extensions=["extra"])
    context = generator.context

    context["teaching"] = load_page_list(
        generator, markdown, "pages/teaching.md", "courses", [("title", True), ("content", False)]
    )
    context["news"] = load_page_list(generator, markdown, "pages/news.md", "entries", [("content", False)])

    context["talks"] = [
        {**talk, "venue": render_markdown(generator, markdown, talk["venue"], "", inline=True)}
        for talk in context["SITE"]["data"]["talks"]
    ]

    for content in context["pages"] + context["articles"]:
        load_latex_macros(content)


def register():
    signals.all_generators_finalized.connect(process)
