# My Academic Website 

This is my academic website. It's a port of
[al-folio](https://github.com/alshedivat/al-folio) adapted for the Python
static site generator [Pelican](https://getpelican.com/). You can find
the Python version of the template [here](https://github.com/vbharadwaj-bk/al-folio-python).

## Content Authoring Extensions

Posts and pages support a few custom Markdown extensions on top of standard
Markdown. They are implemented by the Markdown preprocessors in
`extensions/template_block.py`, and the Jinja helpers callable from them live in
`extensions/md_jinja_extensions.py`.

> Note: content caching is disabled (`LOAD_CONTENT_CACHE = False` in
> `pelicanconf.py`) so that changes to these extensions always take effect on
> the next build. `make clean` also clears the `cache/` directory.

### `{{ ... }}` — inline Jinja

Any `{{ ... }}` region in Markdown is rendered as a Jinja expression. It may
span multiple lines and call any registered helper or filter, so you can express
arbitrary presentation logic inline:

```jinja
{{ md_figure("images/blog/foo.png", "small", "Alt text", "A caption.") }}
```

Available helpers (see `extensions/md_jinja_extensions.py`):

- **`md_figure(path, size="small", caption=None, hover=None, bg_color=None)`** —
  a single, horizontally-centered image on a transparent card (so transparent
  SVGs blend into the page).
  - `path` — image path under `content/`.
  - `size` — the image width; the remaining horizontal space becomes equal
    gutters on either side:

    | `size`   | width (of 12 cols) | gutter each side |
    |----------|--------------------|------------------|
    | `tiny`   | 4                  | 4                |
    | `small`  | 6 (default)        | 3                |
    | `medium` | 8                  | 2                |
    | `large`  | 12 (full width)    | 0                |

  - `caption` — text shown beneath the image. Omit it for no caption.
  - `hover` — tooltip / alt text. Defaults to `caption` when not given.
  - `bg_color` — image background color. When `None` (default) the image is
    transparent inline and takes the page background color when magnified
    (so a clicked/zoomed transparent SVG isn't see-through). Pass `"white"`
    or a hex color (e.g. `"#1b1b1b"`) to force that color in both states.
- **`figure(path, ...)`** — the raw al-folio figure macro (from
  `_includes/figure.html`), auto-imported into every block for fine-grained
  control (class, width/height, zoomable, etc.).

To add a new helper, write a function in `md_jinja_extensions.py` and register
it in `register_md_globals`.

### `!TEMPLATE!` — multi-line Jinja blocks

Fence a region between `!TEMPLATE!` markers to run a full Jinja *template*
(statements like `{% for %}` / `{% set %}`, not just a single expression). The
`figure` macro is auto-imported when the block references it.

```jinja
!TEMPLATE!
{% set courses = ["A", "B", "C"] %}
<ul>{% for c in courses %}<li>{{ c }}</li>{% endfor %}</ul>
!TEMPLATE!
```

### `!FIGURECARD!` — a figure card from YAML

Fence a YAML mapping between `!FIGURECARD!` markers to render a figure inside a
card with explicit column control:

```yaml
!FIGURECARD!
path: images/blog/foo.png
col: 8            # image width, 1–12 (default 8)
left_col: 2       # optional left gutter (defaults to centering)
right_col: 2      # optional right gutter
title: "Title"
caption: "Caption text."
zoomable: true
class: "img-fluid rounded z-depth-1"
card_class: "card border-0 bg-white p-1 mb-3"
!FIGURECARD!
```

### Math

LaTeX math is rewritten for MathJax: inline `$ ... $` becomes `\( ... \)` and
display `$$ ... $$` becomes `\[ ... \]`.

## Image Minification

Use the root script `minify.py` to interactively minify large images in `content/images`.

```bash
python minify.py
python minify.py --threshold-kb 1024 --filter group
python minify.py --revert
```
