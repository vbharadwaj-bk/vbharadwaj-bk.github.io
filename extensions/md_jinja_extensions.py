"""
Custom Jinja helpers available inside Markdown ``{{ ... }}`` blocks.

Posts can drop a Jinja expression straight into Markdown, e.g.::

    {{ md_figure("images/blog/foo.png", "small", "alt text", "a caption") }}

Every callable registered here via :func:`register_md_globals` becomes a global
in the Jinja environment that the Markdown preprocessor (see
``extensions/template_block.py``) uses to render those blocks. To add a new
helper, write a function below and register it in ``register_md_globals``.
"""

from __future__ import annotations

import re
from textwrap import dedent

from jinja2 import Environment


# Bootstrap-style column widths (out of 12) for the supported figure sizes.
SIZE_TO_COL = {
    "tiny": 4,
    "small": 6,
    "medium": 8,
    "large": 12,
}

# bg_color must be the literal "white" or a 3-/6-digit hex color.
_HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def register_md_globals(env: Environment) -> None:
    """Register every Markdown Jinja helper as a global on ``env``."""
    env.globals["md_figure"] = _make_md_figure(env)


def _make_md_figure(env: Environment):
    """Build the ``md_figure`` helper bound to the given Jinja ``env``."""

    template = env.from_string(_MD_FIGURE_TEMPLATE)

    def md_figure(path, size="small", caption=None, hover=None, bg_color=None):
        """Render a single, horizontally-centered image.

        ``size`` (``tiny`` / ``small`` / ``medium`` / ``large``) controls how
        wide the image is; the remaining horizontal space is split into equal
        gutters.

        ``caption`` is shown beneath the image. ``hover`` is the tooltip/alt
        text; when omitted it falls back to ``caption``.

        ``bg_color`` sets the image background. When ``None`` (the default) the
        image is transparent inline and picks up the page background color when
        magnified (so transparent SVGs stay legible). Pass ``"white"`` or a hex
        color (e.g. ``"#1b1b1b"``) to force that color in both states.
        """
        if not path:
            raise ValueError("'path' cannot be empty.")
        if size not in SIZE_TO_COL:
            raise ValueError("'size' must be one of: tiny, small, medium, large.")
        if bg_color is not None and bg_color != "white" \
                and not _HEX_COLOR_RE.match(bg_color):
            raise ValueError("'bg_color' must be 'white' or a hex color like '#1b1b1b'.")

        if hover is None:
            hover = caption

        col = SIZE_TO_COL[size]
        left_col = max((12 - col) // 2, 0)
        right_col = max(12 - col - left_col, 0)

        return template.render(
            path=path,
            caption=caption,
            hover=hover,
            bg_color=bg_color,
            col=col,
            left_col=left_col,
            right_col=right_col,
        ).strip()

    return md_figure


# The card is transparent by default so images with transparent backgrounds
# (e.g. SVGs) blend into the page rather than sitting on a white rectangle.
# The md-figure-img class lets us give the image a solid background when it is
# magnified (see _base.scss); bg_color, when given, overrides that inline.
_MD_FIGURE_TEMPLATE = dedent('''
    {% from "figure.html" import figure with context %}
    <div class="row">
    {% if left_col > 0 %}
        <div class="col-{{ left_col }}"></div>
    {% endif %}
        <div class="col-{{ col }} card border-0 md-figure-card p-1 mb-3">
        {{ figure(path=path, alt=hover, title=hover, caption=caption, class="img-fluid rounded z-depth-1 md-figure-img", zoomable=True, style=("background-color: " ~ bg_color ~ ";" if bg_color else none)) }}
        </div>
    {% if right_col > 0 %}
        <div class="col-{{ right_col }}"></div>
    {% endif %}
    </div>
''')
