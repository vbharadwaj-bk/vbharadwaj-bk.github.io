import shlex
import webbrowser

from invoke import task
from invoke.main import program
from livereload import Server
from pelican import main as pelican_main
from pelican.settings import DEFAULT_CONFIG, get_settings_from_file

SETTINGS_FILE = "pelicanconf.py"
HOST = "localhost"
PORT = 8000

SETTINGS = {**DEFAULT_CONFIG, **get_settings_from_file(SETTINGS_FILE)}


def pelican_build():
    pelican_main(shlex.split(f"-s {SETTINGS_FILE} {program.core.remainder}"))


@task
def livereload(_context):
    """Rebuild the site and reload the browser tab when a source file changes."""
    pelican_build()

    theme, content = SETTINGS["THEME"], SETTINGS["PATH"]
    watched = [SETTINGS_FILE, f"{theme}/templates/**/*.html"]
    watched += [f"{content}/**/*{extension}" for extension in (".md", ".yaml", ".bib")]
    watched += [f"{theme}/static/**/*{extension}" for extension in (".css", ".js")]

    server = Server()
    for pattern in watched:
        server.watch(pattern, pelican_build)

    webbrowser.open(f"http://{HOST}:{PORT}")
    server.serve(host=HOST, port=PORT, root=SETTINGS["OUTPUT_PATH"])
