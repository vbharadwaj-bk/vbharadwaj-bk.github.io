import os
import sys
from datetime import datetime

import yaml

sys.path.append(".")

from extensions import cv_generator, site_data
from extensions.booktabs import BooktabsExtension
from extensions.cache_buster import bust_file_cache
from extensions.filters import display_title
from extensions.parse_bib import parse_bibliography
from extensions.template_block import TemplateBlockExtension
from extensions.toc_md_reader import TOCMarkdownReader
from extensions.urls_dev import absolute_url, relative_url

with open("content/config.yaml", "rb") as stream:
    SITE = yaml.safe_load(stream)

AUTHOR = " ".join(SITE[f] for f in ["first_name", "middle_name", "last_name"] if SITE.get(f))
SITENAME = SITE["title"] or AUTHOR
SITEURL = ""

THEME = "theme"
PATH = "content"
TIMEZONE = "America/Ensenada"
DEFAULT_LANG = "en"

PLUGINS = ["pelican.plugins.sitemap", site_data, cv_generator]
READERS = {"md": TOCMarkdownReader}
JINJA_ENVIRONMENT = {"trim_blocks": True, "lstrip_blocks": True, "extensions": ["jinja2.ext.do"]}

NAV = [
    ("About", ""),
    ("Publications", "publications/"),
    ("Talks", "talks/"),
    ("Teaching", "teaching/"),
    ("Dissertation", "dissertation/"),
    ("Blog", "posts/"),
    ("CV", "cv/"),
]

CV_TEMPLATE_PATH = os.path.join("cv_template", "cv.typst")
CV_PDF_OUTPUT = "cv.pdf"

ARTICLE_PATHS = ["posts"]
ARTICLE_URL = "posts/{date:%Y}/{slug}/"
ARTICLE_SAVE_AS = "posts/{date:%Y}/{slug}/index.html"
INDEX_SAVE_AS = "posts/index.html"
CATEGORY_URL = "posts/category/{slug}/"
CATEGORY_SAVE_AS = "posts/category/{slug}/index.html"
CATEGORIES_SAVE_AS = "posts/category/index.html"
TAG_URL = "posts/tag/{slug}/"
TAG_SAVE_AS = "posts/tag/{slug}/index.html"
TAGS_SAVE_AS = "posts/tag/index.html"
YEAR_ARCHIVE_URL = "posts/{date:%Y}/"
YEAR_ARCHIVE_SAVE_AS = "posts/{date:%Y}/index.html"
AUTHOR_SAVE_AS = AUTHORS_SAVE_AS = ARCHIVES_SAVE_AS = ""

PAGE_PATHS = ["pages"]
PATH_METADATA = r"(?P<path_no_ext>.*)\..*"
PAGE_URL = "{path_no_ext}/"
PAGE_SAVE_AS = "{path_no_ext}/index.html"
STATIC_PATHS = ["images", "pdf", "json"]

DEFAULT_PAGINATION = 5
PAGINATED_TEMPLATES = {"index": None, "tag": 10, "category": 10, "period_archives": 10}
PAGINATION_PATTERNS = (
    (1, "{base_name}", "{base_name}/index.html"),
    (2, "{base_name}/page/{number}/", "{base_name}/page/{number}/index.html"),
)

FEED_ALL_ATOM = CATEGORY_FEED_ATOM = TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = AUTHOR_FEED_RSS = None
FORMATTED_FIELDS = []
LOAD_CONTENT_CACHE = False
CACHE_CONTENT = False

SITE["time"] = datetime.now()
parse_bibliography("content/publications.bib", "publications", SITE)


def jinja_filters(relative_url, absolute_url):
    return {
        "relative_url": relative_url,
        "absolute_url": absolute_url,
        "bust_file_cache": bust_file_cache,
        "display_title": display_title,
    }


def markdown_settings(filters):
    return {
        "extensions": [
            "codehilite", "extra", "meta", "admonition", "toc",
            TemplateBlockExtension(filters=filters), BooktabsExtension(),
        ],
        "extension_configs": {"codehilite": {"css_class": "highlight"}},
        "output_format": "html5",
    }


JINJA_FILTERS = jinja_filters(relative_url, absolute_url)
MARKDOWN = markdown_settings(JINJA_FILTERS)

SITEMAP = {
    "format": "xml",
    "priorities": {"pages": 0.7, "indexes": 0.5, "articles": 0.3},
    "changefreqs": {"indexes": "daily", "pages": "monthly", "articles": "monthly"},
    "exclude": [r"posts/\d+/$", "posts/category/", "posts/page/", "posts/tag/", "404.html$"],
}
