# My Academic Website 

This is my academic website. It's a port of
[al-folio](https://github.com/alshedivat/al-folio) adapted for the Python
static site generator [Pelican](https://getpelican.com/). You can find
the Python version of the template [here](https://github.com/vbharadwaj-bk/al-folio-python).

## Image Minification

Use the root script `minify.py` to interactively minify large images in `content/images`.

```bash
python minify.py
python minify.py --threshold-kb 1024 --filter group
python minify.py --revert
```
