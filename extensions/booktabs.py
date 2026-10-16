from __future__ import annotations

import re
from dataclasses import dataclass, field

from markdown import Extension, Markdown
from markdown.preprocessors import Preprocessor

from extensions.template_block import MathBlockPreprocessor

TABLE_BLOCK = re.compile(r"^!TABLE![ ]*\n(?P<body>.*?)(?<=\n)!TABLE![ ]*$", re.MULTILINE | re.DOTALL)
MIDRULE = re.compile(r"^-{3,}$")
CMIDRULE = re.compile(r"^-{3,}\s+(\d+)-(\d+)$")


@dataclass
class Row:
    cells: list[str]
    midrule: bool = False
    cmidrules: list[tuple[int, int]] = field(default_factory=list)


def split_cells(line):
    cells, current = [], []
    in_math = in_code = False
    index = 0
    while index < len(line):
        char = line[index]
        plain = not in_math and not in_code
        if plain and char == "\\" and line[index + 1:index + 2] == "|":
            current.append("|")
            index += 2
            continue
        if plain and char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            if char == "`" and not in_math:
                in_code = not in_code
            elif char == "$" and not in_code:
                in_math = not in_math
            current.append(char)
        index += 1
    cells.append("".join(current).strip())
    return cells


def parse_rows(body):
    rows, midrule, cmidrules = [], False, []
    for line in (line.strip() for line in body.splitlines()):
        if not line:
            continue
        if MIDRULE.match(line):
            midrule = True
        elif span := CMIDRULE.match(line):
            cmidrules.append((int(span.group(1)), int(span.group(2))))
        else:
            rows.append(Row(split_cells(line), midrule and bool(rows), cmidrules if rows else []))
            midrule, cmidrules = False, []
    return rows


class MathExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(MathBlockPreprocessor(md), "math_block", 15)


class BooktabsPreprocessor(Preprocessor):
    def __init__(self, md):
        super().__init__(md)
        self.cell_markdown = Markdown(extensions=[MathExtension()])

    def render_cell(self, text):
        html = self.cell_markdown.reset().convert(text)
        return html[3:-4] if html.startswith("<p>") and html.endswith("</p>") else html

    def render_row(self, row, width):
        cells = row.cells + [""] * (width - len(row.cells))
        rendered = []
        for column, text in enumerate(cells, start=1):
            ruled = any(first <= column <= last for first, last in row.cmidrules)
            attribute = ' class="cmidrule"' if ruled else ""
            rendered.append(f"<td{attribute}>{self.render_cell(text)}</td>")
        attribute = ' class="midrule"' if row.midrule else ""
        return f"<tr{attribute}>{''.join(rendered)}</tr>"

    def render_table(self, body):
        rows = parse_rows(body)
        width = max((len(row.cells) for row in rows), default=0)
        body_html = "".join(self.render_row(row, width) for row in rows)
        return f'<table class="booktabs"><tbody>{body_html}</tbody></table>'

    def run(self, lines):
        text = "\n".join(lines)
        while match := TABLE_BLOCK.search(text):
            placeholder = self.md.htmlStash.store(self.render_table(match.group("body")))
            text = f"{text[:match.start()]}\n\n{placeholder}\n\n{text[match.end():]}"
        return text.split("\n")


class BooktabsExtension(Extension):
    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.preprocessors.register(BooktabsPreprocessor(md), "booktabs", 24)
