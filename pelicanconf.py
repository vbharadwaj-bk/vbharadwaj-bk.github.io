import yaml
import sys, os
from datetime import datetime
sys.path.append('.')

from extensions.cache_buster import *
from extensions.render_main_scss import *
from extensions.slugify import *
from extensions.parse_bib import *
from extensions.toc_md_reader import TOCMarkdownReader
from extensions.filter_projects import filter_projects 
from extensions.template_block import *
from extensions import al_folio_extension 
from extensions import cv_generator
from extensions.urls_dev import relative_url, absolute_url

SITE = None
with open("content/config.yml", "rb") as stream:
    SITE = yaml.safe_load(stream)

PLUGINS = [
           'pelican.plugins.webassets',
           'pelican.plugins.sitemap',
           al_folio_extension,
           cv_generator,
           ]

name_fields = ["first_name", "middle_name", "last_name"]
AUTHOR = ' '.join([SITE[field] for field in name_fields if field in SITE and SITE[field] is not None])

SITENAME = SITE["title"]

if SITENAME is None:
    SITENAME = AUTHOR
SITEURL = ''

THEME = 'al_folio_theme'
PATH = 'content'

CV_DATA_PATH = os.path.join(PATH, 'cv.yaml')
CV_TEMPLATE_PATH = os.path.join('cv_template', 'cv.typst')
CV_PDF_OUTPUT = 'cv.pdf'

TIMEZONE = 'America/Ensenada'

DEFAULT_LANG = 'en'

ARTICLE_URL = 'posts/{date:%Y}/{slug}/'
ARTICLE_SAVE_AS = 'posts/{date:%Y}/{slug}/index.html'

FORMATTED_FIELDS = []

if SITE["blog_enabled"]:
    INDEX_SAVE_AS = '/posts/index.html'
    ARTICLE_PATHS=['posts']

    CATEGORY_URL = 'posts/category/{slug}/'
    CATEGORY_SAVE_AS = 'posts/category/{slug}/index.html'

    TAG_URL = 'posts/tag/{slug}/'
    TAG_SAVE_AS = 'posts/tag/{slug}/index.html'

    YEAR_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/index.html'
    PAGINATED_TEMPLATES = {'index': None, 'tag': 10, 'category': 10, 'author': 10, 'period_archives': 10}

    CATEGORIES_SAVE_AS = 'posts/category/index.html'
    TAGS_SAVE_AS = 'posts/tag/index.html'

else:
    INDEX_SAVE_AS = ''
    ARTICLE_PATHS=[]

    CATEGORY_URL = ''
    CATEGORY_SAVE_AS = ''

    TAG_URL = ''
    TAG_SAVE_AS = ''

    PAGINATED_TEMPLATES = {}
    FORMATTED_FIELDS = []

    CATEGORIES_SAVE_AS = ''
    TAGS_SAVE_AS = ''

# Suppress generation of these pages.
AUTHOR_URL = AUTHOR_SAVE_AS = ''
AUTHORS_SAVE_AS = ''
ARCHIVES_SAVE_AS = ''


PAGE_PATHS = ['pages', 'projects']
PATH_METADATA = r'(?P<path_no_ext>.*)\..*'
PAGE_URL = '{path_no_ext}/'
PAGE_SAVE_AS = '{path_no_ext}/index.html'

STATIC_PATHS = ['images', 'pdf', 'json']

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

DEFAULT_PAGINATION = 5 
PAGINATION_PATTERNS = (
    (1, '{base_name}', '{base_name}/index.html'),
    (2, '{base_name}/page/{number}/', '{base_name}/page/{number}/index.html'),
)

# Should extend to getting all data from the folder
SITE["data"] = {}

for data_name in ["venues", "coauthors", "talks"]:
    with open(f"content/data/{data_name}.yml", "rb") as stream:
        SITE["data"][data_name] = yaml.safe_load(stream)

SITE["time"] = datetime.now()
parse_bibliography("content/publications.bib", "publications", SITE)

with open("content/cv.yaml", "rb") as stream:
    SITE["data"]["cv"] = cv_generator.build_al_folio_cv_data(
        yaml.safe_load(stream), SITE.get("publications")
    )

render_main_scss(SITE)

JINJA_FILTERS = {
                'relative_url': relative_url, 
                'absolute_url': absolute_url, 
                'bust_file_cache': bust_file_cache,
                'slugify': slugify,
                'filter_projects': filter_projects
                }

MARKDOWN = {
    'extensions': ['codehilite', 'extra', 'meta', 'admonition', 'toc',
                   TemplateBlockExtension(filters=JINJA_FILTERS)],
    'extension_configs': {
        'codehilite': {'css_class': 'highlight'},
        'extra': {'attr_list': {}},
        'meta': {},
        'admonition': {},
        'toc': {}
    },
    'output_format': 'html5',
}

# Content is rendered through custom Markdown extensions (see
# extensions/template_block.py) whose logic can change independently of the
# source files. Pelican's content cache keys only on file mtime, so it would
# happily serve stale HTML after an extension change. The site builds in well
# under a second, so we disable the cache to keep builds always-correct.
LOAD_CONTENT_CACHE = False
CACHE_CONTENT = False

SITEMAP = {
    "format": "xml",
    "priorities": {
        "pages": 0.7,
        "indexes": 0.5,
        "articles": 0.3
    },
    "changefreqs": {
        "indexes": "daily",
        "pages": "monthly",
        "articles": "monthly",
    },
    "exclude": [
            "^/noindex/",  # starts with "/noindex/"
            r"posts/\d+/$",
            "posts/category/",
            "posts/page/",
            "posts/tag/",
            "404.html$",
        ]
}

READERS = {'md': TOCMarkdownReader}
