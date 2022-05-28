import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, Template
from jinja2.exceptions import TemplateNotFound


def _find_template_directories(root_dir: str, template_dir_name: str) -> List[str]:
    """Find the directories that possibly contain templates.

    This function does not check if the directories actually contain templates. It only
    finds directories that with name matching the given `template_dir_name`.

    Arguments:
        root_dir (str): The root directory to start searching from.
        template_dir_name (str): The name of the directories to find.

    Returns:
        (List[str]): The list of directories that possibly contain templates.
    """
    result = []
    for rootdir, dirs, _ in os.walk(root_dir):
        for subdir in dirs:
            if subdir == template_dir_name:
                result.append(os.path.join(rootdir, subdir))

    return result


class BaseTemplateEngine(ABC):
    """The base template engine class.

    The template engine is responsible for loading templates and rendering them.

    This class can be subclassed to implement a custom template engine.
    """

    def __init__(
        self, root_dir: str = None, template_dir_name: Optional[str] = "templates"
    ):
        if not root_dir or not os.path.isdir(root_dir):
            raise FileNotFoundError(f"{root_dir} is not a directory.")

        self._root_dir = root_dir
        self._template_dir_name = template_dir_name

    @abstractmethod
    def render(self, template_name: str, context: Optional[Dict] = None) -> Any:
        """Render a template.

        Information provided in the `context` dictionary will be available in the
        template.

        Arguments:
            template_name (str): The name of the template to render.
            context (Optional[Dict]): The context to use when rendering the template.

        Returns:
            Any: The rendered template.
        """

    @abstractmethod
    def has_template(self, template_name: str) -> bool:
        """Check if the template engine has a template with the given name.

        Arguments:
            template_name (str): The name of the template to check.

        Returns:
            bool: True if the template engine has a template with the given name,
                False otherwise.
        """


class JinjaTemplateEngine(BaseTemplateEngine):
    """The Jinja template engine class.

    The template engine is responsible for loading templates and rendering them. This
    engine uses Jinja2 library to load, parse, and render templates.
    """

    def __init__(
        self, root_dir: str = None, template_dir_name: Optional[str] = "templates"
    ):
        super().__init__(root_dir, template_dir_name)

        self._env = Environment(
            loader=FileSystemLoader(
                _find_template_directories(root_dir, template_dir_name)
            )
        )

    def render(self, template_name: str, context: Optional[Dict] = None) -> Template:
        """Render a template.

        Information provided in the `context` dictionary will be available in the
        template.

        Arguments:
            template_name (str): The name of the template to render.
            context (Optional[Dict]): The context to use when rendering the template.

        Returns:
            Template: The rendered template.
        """
        if context is None:
            context = {}

        try:
            return self._env.get_template(template_name).render(**context).encode()
        except TemplateNotFound as ex:
            raise FileNotFoundError(f"{template_name} is not found.") from ex

    def has_template(self, template_name: str) -> bool:
        """Check if the template engine has a template with the given name.

        Arguments:
            template_name (str): The name of the template to check.

        Returns:
            bool: True if the template engine has a template with the given name,
                False otherwise.
        """
        return template_name in self._env.loader.list_templates()


__all__ = ["BaseTemplateEngine", "JinjaTemplateEngine"]
