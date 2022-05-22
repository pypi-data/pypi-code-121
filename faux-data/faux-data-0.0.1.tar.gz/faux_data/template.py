from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import List, Tuple

import yaml

from .table import Table
from .template_rendering import render_template


@dataclass(kw_only=True)
class Template:
    variables: dict = field(default_factory=dict, repr=False)
    tables: List[Table]
    params: dict = field(default_factory=dict, init=False, repr=False)

    def __init__(self, tables: dict, variables: dict = None):
        self.tables = [Table(**table) for table in tables]

    def generate(self):
        for table in self.tables:
            table.generate()

    def run(self):
        for table in self.tables:
            table.run()

    def result(self):
        return '/n'.join(t.result() for t in self.tables)

    @classmethod
    def from_string(cls, template_str, params={}) -> Template:
        rendered_template, _ = cls.render_template(template_str, params)
        parsed = yaml.safe_load(rendered_template)
        return cls(**parsed)

    @classmethod
    def from_base64_string(cls, base64_str) -> Template:
        template_str = base64.b64decode(base64_str).decode('utf-8')
        return cls.from_string(template_str)

    @classmethod
    def from_file(cls, filepath, params={}):
        with open(filepath, "r") as f:
            template_str = f.read()
        return cls.from_string(template_str, params)

    @classmethod
    def render_template(cls,
                        template_str,
                        params={}) -> Tuple[str, dict[str:str]]:
        """Renders a template string using the provided `params`."""
        return render_template(template_str, params)

    @classmethod
    def render_from_file(cls, filepath, params) -> Tuple[str, dict[str:str]]:
        with open(filepath, "r") as f:
            template_str = f.read()
        return cls.render_template(template_str, params)

    def __repr__(self):
        tables = '\n'.join(table.__repr__() for table in self.tables)
        return f"""
TEMPLATE
{tables}
"""
