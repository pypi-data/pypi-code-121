"""Promail template Abstract."""
import abc
import json
import os
import sys
import webbrowser
from io import StringIO
from typing import AnyStr, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from jsonschema import validate  # type: ignore

from mjml import mjml_to_html

from promail_template.utilities.schema_generation import SchemaGen


class PromailTemplate(abc.ABC):
    """Object for creating Email templates."""

    sample_filename = "sample.json"
    schema_filename = "schema.json"
    mjml_filename = "template.mjml"

    # class Methods

    @classmethod
    def path(cls) -> str:
        """Gets absolute path of the directory class's directory."""
        mypath = os.path.dirname(str(sys.modules[cls.__module__].__file__))
        return mypath

    @classmethod
    def mjml_path(cls) -> AnyStr:
        """Get Absolute path to template.mjml file."""
        return cls.absolute_path(cls.mjml_filename)

    @classmethod
    def sample_path(cls) -> AnyStr:
        """Get Absolute path to sample.json file."""
        return cls.absolute_path(cls.sample_filename)

    @classmethod
    def sample_data(cls) -> dict:
        """Get Sample Data."""
        with open(cls.sample_path(), "r") as json_file:
            return json.load(json_file)

    @classmethod
    def schema_path(cls) -> AnyStr:
        """Get Absolute path to schema.json file."""
        return cls.absolute_path(cls.schema_filename)

    @classmethod
    def absolute_path(cls, relative_path):
        """Get absolute path to specified file within template directory."""
        return os.path.join(cls.path(), relative_path)

    @classmethod
    def schema(cls) -> dict:
        """Get template schema."""
        with open(cls.schema_path(), "r") as file:
            return json.load(file)

    @classmethod
    def generate_schema(cls, data: dict) -> dict:
        """Generate schema from provided data."""
        schema_builder = SchemaGen()
        schema_builder.add_object(data)
        return schema_builder.to_schema()

    @classmethod
    def save_schema(cls, data: dict) -> None:  # pragma: no cover
        """Generate schema from provided data."""
        schema = cls.generate_schema(data)
        with open(cls.schema_path(), "w") as json_file:
            json.dump(schema, json_file)

    @classmethod
    def validate_data(cls, data: dict) -> None:
        """Checks that data provided matches schema, raises error if not."""
        validate(instance=data, schema=cls.schema())

    # instance methods
    def __init__(self, data: dict = None, json_filepath: str = None):
        """Initialize Promail Template."""
        if data is None:
            if json_filepath is None:
                # if no data or json_filepath is provided we use the sample data
                json_filepath = self.sample_path()

            with open(json_filepath, "r") as jsonfile:
                self.user_data = json.load(jsonfile)

        else:
            self.user_data = data

        self._context = None
        self._mjml = None
        self._errors = None
        self._html = None

    @property
    def env(self):
        """Get Jinja environment."""
        return Environment(
            loader=FileSystemLoader(searchpath=self.path()),
            autoescape=select_autoescape(["mjml"]),
        )

    @property
    def context(self) -> Optional[dict]:
        """Processes user data and expands on referenced fields (such as csv)."""
        if self._context is None:  # pragma: no cover
            self._context = self.user_data  # todo: Process CSVs
        return self._context

    @property
    def mjml(self):
        """Get mjml text."""
        if self._mjml is None:  # pragma: no cover
            template = self.env.get_template(self.mjml_filename)
            self._mjml = template.render(
                **self.context
            )  # this is where to put args to the template renderer
        return self._mjml

    @property
    def html(self):
        """Get rendered html text."""
        if self._html is None:  # pragma: no cover
            render_html = mjml_to_html(StringIO(self.mjml))
            self._html = render_html["html"]
            self._errors = render_html["errors"]
        return self._html

    def save_preview_html(self, path: str):  # pragma: no cover
        """Saves a copy of html code at specified path."""
        with open(path, "w") as file:
            file.write(self.html)

    def preview_html(self, filename: str = "preview.html"):  # pragma: no cover
        """Preview html in web browser."""
        path = os.path.join(os.getcwd(), filename)
        self.save_preview_html(path)
        url = "file://" + path
        webbrowser.open(url)
