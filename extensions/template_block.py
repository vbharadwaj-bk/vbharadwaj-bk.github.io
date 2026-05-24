from __future__ import annotations

from textwrap import dedent
import yaml
from markdown import Extension
from markdown.preprocessors import Preprocessor
from markdown.serializers import _escape_attrib_html
import re

from jinja2 import Environment, FileSystemLoader

from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree


class TemplateBlockExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'filters': ['filters-', 'JINJA filters to include in environment. Default: None.']
        }
        """ Default configuration options. """
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        """ Add `FencedBlockPreprocessor` to the Markdown instance. """
        md.registerExtension(self)
        md.preprocessors.register(TemplateBlockPreprocessor(md, self.getConfigs()), 'template_block', 175)
        md.preprocessors.register(MathBlockPreprocessor(md, self.getConfigs()), 'math_block', 15)

class TemplateBlockPreprocessor(Preprocessor):
    """ 
    Find and extract template blocks.
    This extension renders any template block it finds 
    using Jinja and outputs an error if template
    rendering fails. 
    """

    TEMPLATE_BLOCK_RE = re.compile(
        dedent(r'''
            (?P<fence>^!TEMPLATE!)[ ]*
            \n                                       # newline (end of opening fence)
            (?P<template>.*?)(?<=\n)                 # the template 
            (?P=fence)[ ]*$                          # closing fence
        '''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

    FIGURE_CARD_BLOCK_RE = re.compile(
        dedent(r'''
            (?P<fence>^!FIGURECARD!)[ ]*
            \n                                       # newline (end of opening fence)
            (?P<params>.*?)(?<=\n)                   # YAML parameters
            (?P=fence)[ ]*$                          # closing fence
        '''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

    INLINE_FIGURE_RE = re.compile(
        dedent(r'''
            ^!figure\((?P<args>.*)\)[ ]*$
        '''),
        re.MULTILINE | re.VERBOSE
    )

    SIZE_TO_COL = {
        "small": 6,
        "medium": 8,
        "large": 12,
    }

    def __init__(self, md, config):
        super().__init__(md)
        self.config = config
        filters = self.config.get('filters', None)
        self.env = Environment(loader=FileSystemLoader(searchpath='al_folio_theme/templates/_includes/'))

        for key in filters:
            self.env.filters[key] = filters[key]

        self.figure_import = '{% from "figure.html" import figure with context %}\n'

    def _render_figure_card(self, params):
        if "path" not in params:
            raise ValueError("Missing required key 'path'.")

        col = int(params.get("col", 8))
        if col < 1 or col > 12:
            raise ValueError("'col' must be between 1 and 12.")

        default_left = max((12 - col) // 2, 0)
        left_col = int(params.get("left_col", default_left))
        right_col = int(params.get("right_col", max(12 - col - left_col, 0)))

        if left_col < 0 or right_col < 0 or (left_col + col + right_col) > 12:
            raise ValueError("Invalid column layout. Ensure left_col + col + right_col <= 12.")

        fig_class = params.get("class", "img-fluid rounded z-depth-1")
        card_class = params.get("card_class", "card border-0 bg-white p-1 mb-3")

        template_input = dedent('''
            <div class="row">
            {% if left_col > 0 %}
                <div class="col-{{ left_col }}"></div>
            {% endif %}
                <div class="col-{{ col }} {{ card_class }}">
                {{ figure(path=path, title=title, class=fig_class, zoomable=zoomable) }}
                {% if caption %}
                <div class="caption">
                {{ caption }}
                </div>
                {% endif %}
            </div>
            {% if right_col > 0 %}
            <div class="col-{{ right_col }}"></div>
            {% endif %}
            </div>
        ''')

        template = self.env.from_string(self.figure_import + template_input)
        return template.render(
            path=params["path"],
            title=params.get("title", ""),
            caption=params.get("caption", ""),
            fig_class=fig_class,
            card_class=card_class,
            col=col,
            left_col=left_col,
            right_col=right_col,
            zoomable=bool(params.get("zoomable", True)),
        )

    def _render_inline_figure(self, args_text):
        args = []
        current = []
        quote_char = None

        for ch in args_text:
            if quote_char is None:
                if ch in ('"', "'"):
                    quote_char = ch
                    current.append(ch)
                elif ch == ',':
                    args.append(''.join(current).strip())
                    current = []
                else:
                    current.append(ch)
            else:
                current.append(ch)
                if ch == quote_char:
                    quote_char = None

        if quote_char is not None:
            raise ValueError("Unterminated quote in !figure arguments.")

        args.append(''.join(current).strip())

        if len(args) != 4:
            raise ValueError("Expected 4 arguments: path, size, alt, caption.")

        path = args[0]
        size = args[1]
        alt_raw = args[2]
        caption_raw = args[3]

        if len(alt_raw) < 2 or alt_raw[0] not in ('"', "'") or alt_raw[-1] != alt_raw[0]:
            raise ValueError("'alt' must be wrapped in matching quotes.")

        if len(caption_raw) < 2 or caption_raw[0] not in ('"', "'") or caption_raw[-1] != caption_raw[0]:
            raise ValueError("'caption' must be wrapped in matching quotes.")

        alt = alt_raw[1:-1].strip()
        caption = caption_raw[1:-1].strip()

        if not path:
            raise ValueError("'path' cannot be empty.")

        size_key = size.lower()
        if size_key not in self.SIZE_TO_COL:
            raise ValueError("'size' must be one of: small, medium, large.")

        col = self.SIZE_TO_COL[size_key]
        left_col = max((12 - col) // 2, 0)
        right_col = max(12 - col - left_col, 0)

        template_input = dedent('''
            <div class="row">
            {% if left_col > 0 %}
                <div class="col-{{ left_col }}"></div>
            {% endif %}
                <div class="col-{{ col }} card border-0 bg-white p-1 mb-3">
                {{ figure(path=path, alt=alt, title=alt, caption=caption, class="img-fluid rounded z-depth-1", zoomable=True) }}
            </div>
            {% if right_col > 0 %}
            <div class="col-{{ right_col }}"></div>
            {% endif %}
            </div>
        ''')

        template = self.env.from_string(self.figure_import + template_input)
        return template.render(
            path=path,
            alt=alt,
            caption=caption,
            col=col,
            left_col=left_col,
            right_col=right_col,
        ).strip()


    def run(self, lines):
        """ Match and store Template Blocks in the `HtmlStash`. """

        text = "\n".join(lines)

        while 1:
            m = self.INLINE_FIGURE_RE.search(text)
            if m:
                args_text = m.group("args")
                try:
                    rendered = self._render_inline_figure(args_text)
                except Exception as e:
                    rendered = f'<p>FIGURE ERROR: {e}</p>'

                text = f'{text[:m.start()]}{rendered}{text[m.end():]}'
            else:
                break

        while 1:
            m = self.FIGURE_CARD_BLOCK_RE.search(text)
            if m:
                params_input = m.group('params')
                try:
                    params = yaml.safe_load(params_input) or {}
                    if not isinstance(params, dict):
                        raise ValueError("FIGURECARD content must be a YAML dictionary.")
                    rendered = self._render_figure_card(params)
                except Exception as e:
                    rendered = f'<p>FIGURECARD ERROR: {e}</p>'

                text = f'{text[:m.start()]}\n{rendered}\n{text[m.end():]}'
            else:
                break

        while 1:
            m = self.TEMPLATE_BLOCK_RE.search(text)
            if m:
                template_input = m.group('template')
                if 'figure(' in template_input:
                    template_input = self.figure_import + template_input
                template_rendered = None
                # Load the template
                try:
                    template = self.env.from_string(template_input)  
                    data = {} 
                    template_rendered = template.render(data)
                except Exception as e:
                    template_rendered = f'<p>JINJA TEMPLATE ERROR: {e}</p>'
                text = f'{text[:m.start()]}\n{template_rendered}\n{text[m.end():]}'

            else:
                break
        return text.split("\n")


class MathBlockPreprocessor(Preprocessor):
    """ 
    Find and extract template blocks.
    This extension renders any template block it finds 
    using Jinja and outputs an error if template
    rendering fails. 
    """

    TEMPLATE_BLOCK_MATH = re.compile(
        dedent(r'''
            (?P<fence>\$\$)
            (?P<mathblock>.*?)                 
            (?P=fence)                        
        '''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

    TEMPLATE_LINE_MATH = re.compile(
        dedent(r'''
            (?P<fence>\$)
            (?P<mathline>[^\$].*?)
            (?P=fence)                      
        '''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

    def __init__(self, md, config):
        super().__init__(md)
        self.config = config

    def run(self, lines):
        """ Match and store Template Blocks in the `HtmlStash`. """

        text = "\n".join(lines)
        while 1:
            m = self.TEMPLATE_BLOCK_MATH.search(text)
            if m:
                mathblock = '\[' + m.group('mathblock') + '\]'
                stash = self.md.htmlStash.store(mathblock)
                text = f'{text[:m.start()]}{stash}{text[m.end():]}'
            else:
                break

        while 1:
            m = self.TEMPLATE_LINE_MATH.search(text)
            if m:
                mathline = '\(' + m.group('mathline') + '\)'
                stash = self.md.htmlStash.store(mathline)
                text = f'{text[:m.start()]}{stash}{text[m.end():]}'
            else:
                break

        return text.split("\n")