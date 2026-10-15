from __future__ import annotations

import re

from jinja2 import Environment

SIZES = ("tiny", "small", "medium", "large")
HEX_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")

MD_FIGURE = """
<figure class="figure {{ size }}">
  <img src="{{ path | bust_file_cache | relative_url }}"
    {%- if hover %} alt="{{ hover | trim }}" title="{{ hover | trim }}"{% endif %}
    {%- if bg_color %} style="background-color: {{ bg_color }};"{% else %} class="zoom-backdrop"{% endif %} data-zoomable loading="lazy">
  {%- if caption %}
  <figcaption>{{ caption | trim }}</figcaption>
  {%- endif %}
</figure>
"""


def register_md_globals(env: Environment) -> None:
    template = env.from_string(MD_FIGURE)

    def md_figure(path, size="small", caption=None, hover=None, bg_color=None):
        if not path:
            raise ValueError("'path' cannot be empty.")
        if size not in SIZES:
            raise ValueError("'size' must be one of: tiny, small, medium, large.")
        if bg_color is not None and bg_color != "white" and not HEX_COLOR.match(bg_color):
            raise ValueError("'bg_color' must be 'white' or a hex color like '#1b1b1b'.")

        hover = caption if hover is None else hover
        return template.render(
            path=path, size=size, caption=caption, hover=hover, bg_color=bg_color
        ).strip()

    env.globals["md_figure"] = md_figure
