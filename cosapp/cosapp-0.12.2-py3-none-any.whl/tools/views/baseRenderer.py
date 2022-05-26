import io
import abc
from typing import Dict
from jinja2.environment import Template

from cosapp.systems import System
from cosapp.utils.helpers import check_arg


class BaseRenderer(metaclass=abc.ABCMeta):
    """
    Base class to export a system as HTML.

    Parameters
    ----------
    system : System
        System to export
    embeddable: bool, optional
        Is the HTML to be embedded in an existing page? Default: False
    """
    def __init__(self, system: System, embeddable=False):
        check_arg(system, "system", System)
        self.system = system
        self.embeddable = embeddable

    @abc.abstractmethod
    def get_data(self, **kwarg) -> Dict:
        """Convert  `self.system` into a dictionary used to build the HTML page.

        Returns
        -------
        Dict
            Dictionary containing elements to create HTML page
        """
        pass

    @abc.abstractmethod
    def html_content(self) -> str:
        """Returns HTML content of renderer's system as a character string."""
        pass

    def dump(self, fstream: io.RawIOBase) -> None:
        """Dump HTML content into writable fstream"""
        rendered_html = self.html_content()
        fstream.write(rendered_html)

    def to_file(self, filename: str) -> None:
        """Dump HTML content into text file `filename`"""
        with open(filename, "w", encoding="utf-8") as fp:
            self.dump(fp)

    @classmethod
    def html_tags(cls) -> Dict[str, str]:
        html_begin_tags = """<!DOCTYPE html>
            <html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <title>{{title}}</title>
            </head>
            <body>\n
        """
        html_end_tags = """
            </body>
            </html>
        """
        return {"html_begin_tags": html_begin_tags, "html_end_tags": html_end_tags}

    @classmethod
    @abc.abstractclassmethod
    def html_resources(cls) -> Dict[str, str]:
        """
        Return the necessary resources to render Jinja template.
        """
        pass

    @classmethod
    @abc.abstractclassmethod
    def html_template(cls) -> Template:
        """
        Return the Jinja template used to create HTML file.
        """
        pass

    @classmethod
    def get_globals(cls) -> Dict:
        """Returns a dict containing class-wide environment and HTML data"""
        return dict(
            template=cls.html_template(),
            **cls.html_tags(),
            **cls.html_resources(),
        )
