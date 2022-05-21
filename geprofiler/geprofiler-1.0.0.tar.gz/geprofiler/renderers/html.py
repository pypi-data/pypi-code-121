from __future__ import annotations

import codecs
import os
import tempfile
import urllib.parse
import webbrowser
from typing import Any

from geprofiler import processors
from geprofiler.renderers.base import ProcessorList, Renderer
from geprofiler.renderers.jsonrenderer import JSONRenderer
from geprofiler.session import Session

# pyright: strict


class HTMLRenderer(Renderer):
    """
    Renders a rich, interactive web page, as a string of HTML.
    """

    output_file_extension = "html"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def render(self, session: Session, json_output: str = ''):
        resources_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html_resources/")

        if not os.path.exists(os.path.join(resources_dir, "app.js")):
            raise RuntimeError(
                "Could not find app.js. If you are running "
                "geprofiler from a git checkout, run 'python "
                "setup.py build' to compile the Javascript "
                "(requires nodejs)."
            )

        with open(os.path.join(resources_dir, "app.js"), encoding="utf-8") as f:
            js = f.read()

        if json_output == '':
            json_output = f"[{self.render_json(session)}]"

        page = """<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
            </head>
            <body>
                <div id="app"></div>
                <script>
                    window.profileSession = {json_output}
                </script>
                <script>
                    {js}
                </script>
            </body>
            </html>""".format(
            js=js, json_output=json_output
        )

        return page

    def open_in_browser(self, session: Session, output_filename: str | None = None):
        """
        Open the rendered HTML in a webbrowser.

        If output_filename=None (the default), a tempfile is used.

        The filename of the HTML file is returned.

        """
        if output_filename is None:
            output_file = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
            output_filename = output_file.name
            with codecs.getwriter("utf-8")(output_file) as f:
                f.write(self.render(session))
            url = urllib.parse.urlunparse(("file", "", output_filename, "", "", ""))
        else:
            with codecs.open(output_filename, "w", "utf-8") as f:
                f.write(self.render(session))
            url = "file:///" + os.getcwd() + "/" + output_filename

        webbrowser.open(url)

    def render_json(self, session: Session):
        json_renderer = JSONRenderer()
        json_renderer.processors = self.processors
        json_renderer.processor_options = self.processor_options
        return json_renderer.render(session)

    def default_processors(self) -> ProcessorList:
        return [
            processors.remove_importlib,
            processors.merge_consecutive_self_time,
            processors.aggregate_repeated_calls,
            processors.group_library_frames_processor,
            processors.remove_unnecessary_self_time_nodes,
            processors.remove_irrelevant_nodes,
        ]
