from jinja2 import Environment

from sila2.code_generator.template_loader import TemplateLoader


class TemplateEnvironment(Environment):
    def __init__(self):
        super().__init__(loader=TemplateLoader(), autoescape=False, keep_trailing_newline=True)
        self.filters["repr"] = repr
        self.filters["strip"] = str.strip
        self.filters["lower"] = str.lower
