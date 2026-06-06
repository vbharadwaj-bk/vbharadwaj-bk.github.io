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

from textwrap import dedent

from jinja2 import Environment


# Bootstrap-style column widths for the supported figure sizes.
SIZE_TO_COL = {
    "small": 6,
    "medium": 8,
    "large": 12,
}


def register_md_globals(env: Environment) -> None:
    """Register every Markdown Jinja helper as a global on ``env``."""
    env.globals["md_figure"] = _make_md_figure(env)


def _make_md_figure(env: Environment):
    """Build the ``md_figure`` helper bound to the given Jinja ``env``."""

    template = env.from_string(_MD_FIGURE_TEMPLATE)

    def md_figure(path, size="small", alt="", caption=""):
        """Render a single, horizontally-centered image.

        ``size`` (``small`` / ``medium`` / ``large``) controls how wide the
        image is; the remaining horizontal space is split into equal gutters.
        """
        if not path:
            raise ValueError("'path' cannot be empty.")
        if size not in SIZE_TO_COL:
            raise ValueError("'size' must be one of: small, medium, large.")

        col = SIZE_TO_COL[size]
        left_col = max((12 - col) // 2, 0)
        right_col = max(12 - col - left_col, 0)

        return template.render(
            path=path,
            alt=alt,
            caption=caption,
            col=col,
            left_col=left_col,
            right_col=right_col,
        ).strip()

    return md_figure


_MD_FIGURE_TEMPLATE = dedent('''
    {% from "figure.html" import figure with context %}
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
