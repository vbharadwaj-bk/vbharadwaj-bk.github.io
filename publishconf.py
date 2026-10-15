import os
import sys

sys.path.append(os.curdir)

from pelicanconf import *

from extensions import urls_publish

JINJA_FILTERS = jinja_filters(*urls_publish.make_functions())
MARKDOWN = markdown_settings(JINJA_FILTERS)

SITEURL = SITE["url"] + ("/" + SITE["baseurl"] if SITE["baseurl"] else "")
RELATIVE_URLS = True
DELETE_OUTPUT_DIRECTORY = True
