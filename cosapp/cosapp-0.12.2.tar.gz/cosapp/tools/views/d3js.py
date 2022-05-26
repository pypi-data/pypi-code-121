"""Build a D3js view of a System."""

import os
from typing import Dict
from cosapp.systems import System
from cosapp.tools import templates
from .baseRenderer import BaseRenderer


class D3JsRenderer(BaseRenderer):
    """
    Utility class to export a system as HTML using D3.JS library.

    Parameters
    ----------
    system : System
        System to export

    embeddable: bool, optional
        Is the HTML to be embedded in an existing page? Default: False
    """
    
    __globals = None

    def __init__(self, system: System, embeddable=False):
        super().__init__(system, embeddable)

    @staticmethod
    def get_level(syst) -> int:
        """
        Return the number of child levels of input system
        """
        if len(syst.children) == 0:
            return 1
        else:
            return 1 + max(map(D3JsRenderer.get_level, syst.children.values()))

    def get_data(self) -> Dict:
        """
        Convert  `self.system` into a dictionary with 4 keys: `name`, `full_name`, `children` and `size`.

        - `name` key is a string with the system name.
        - `full_name` key is a string with Module contextual name.
        - `children` key is a list containing dictionaries of same format for children system .
        - `size` key is the display size of system in D3 plot.

        Returns
        -------
        Dict
            Dictionary containing elements to draw the `System` using D3JS library
        """

        def build_d3_json(
            system: System, parent_name: str = None, nlevels: int = 0
        ) -> Dict[str, Dict]:
            """
            Builds the dictionary of system structure for D3 plot.

            Parameters
            ----------
            system : System
                Current input system

            parent_name : str, optional
                Name of parent system, default None

            nlevels : int, optional
                Number of system levels, default 0

            Returns
            -------
            Dict[str, Dict]
                The structure of input system in D3 format
            """
            if parent_name is None:
                full_name = system.name
            else:
                full_name = f"{parent_name}.{system.name}"

            if nlevels == 0:  # Number of System levels
                nlevels = D3JsRenderer.get_level(system)

            level = len(full_name.split("."))

            rtn = {"name": system.name, "full_name": full_name}
            if system.children:
                rtn["children"] = [
                    build_d3_json(child, parent_name=full_name, nlevels=nlevels)
                    for child in system.children.values()
                ]
            else:
                rtn["size"] = (nlevels / level) ** 5

            return rtn

        return build_d3_json(self.system)

    @classmethod
    def html_resources(cls) -> Dict[str, str]:
        """
        Return a dictionary of three keys.

        - `d3_js` key holds the content of D3.js library.
        - `draw_js` key holds the content of the draw function implemented in `d3_draw.js`.
        - `d3_styles` key holds the css style of D3 plot.

        Returns
        -------
        Dict[str, Dict]
            The necessary resources to render Jinja template
        """
        ressource_dir = os.path.dirname(os.path.abspath(templates.__file__))
        libs_dir = os.path.join(ressource_dir, "lib")
        src_dir = os.path.join(ressource_dir, "src")
        # Grab the resources
        with open(os.path.join(libs_dir, "d3.min.js"), "r", encoding="utf-8") as f:
            d3_js = f.read()
        with open(os.path.join(src_dir, "d3_draw.js"), "r", encoding="utf-8") as f:
            draw_js = f.read()
        with open(os.path.join(src_dir, "d3_styles.css"), "r", encoding="utf-8") as f:
            d3_styles = f.read()

        return {"d3_js": d3_js, "draw_js": draw_js, "d3_styles": d3_styles}

    @classmethod
    def html_template(cls) -> "Template":
        """
        Return the Jinja template used to create HTML file.

        Returns
        -------
        Template

        """
        try:
            from jinja2 import Environment, PackageLoader
        except ImportError:
            raise ImportError("jinja2 needs to be installed to export to d3 JS.")

        env = Environment(
            loader=PackageLoader("cosapp.tools", "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template("system_d3.html")

        return template

    def html_content(self) -> str:
        """
        Return D3 HTML content of renderer's system as a character string.

        Returns
        -------
        str

        """
        common = self.get_globals()
        template = common["template"]
        html_begin_tags = common["html_begin_tags"] + "\n<div class='flexdiv'>"
        html_end_tags = common["html_end_tags"]
        d3_js = common["d3_js"]
        draw_js = common["draw_js"]
        d3_styles = common["d3_styles"]

        elements = {
            "title": "my viewer",
            "model_data": f"var modelData = {self.get_data()!s}",
            "d3_styles": d3_styles,
            "d3JS": d3_js,
            "draw": draw_js,
        }

        rendered_html = template.render(elements)
        if not self.embeddable:
            html_begin_tags = html_begin_tags.replace("{{title}}", elements["title"])
            rendered_html = html_begin_tags + rendered_html + html_end_tags

        return rendered_html
    
    @classmethod
    def get_globals(cls):
        cg = cls.__globals
        if cg is None:
            cg = super().get_globals()
        return cg


def d3_html(system: System, embeddable=False) -> str:
    """Return D3.JS HTML content of `system`.

    Parameters
    ----------
    system : System
        System to export

    embeddable: bool, optional
        Is the HTML to be embedded in an existing page? Default: False
    """
    renderer = D3JsRenderer(system, embeddable)
    return renderer.html_content()


def to_d3(system: System, show: bool = True, size=435) -> None:
    """Return the representation of this system in HTML format.

    Returns
    -------
    str
        HTML formatted representation
    """

    filename = f"{system.name}.html"
    rendered_html = d3_html(system, embeddable=False)
    with open(filename, mode="w", encoding="utf-8") as f:
        f.write(rendered_html)

    if show:
        try:
            from IPython.display import IFrame
        except ImportError:
            raise ImportError("IPython needs to be installed to display the d3 figure.")
        return IFrame(filename, "99.9%", f"{size}px")
    else:
        return None
