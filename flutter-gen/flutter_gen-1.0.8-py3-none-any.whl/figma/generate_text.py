from jinja2 import Environment, PackageLoader
from ..core.constants import CSS_METHOD
from ..utils.utils import logResult
from ..core.command import Command
import cssutils


class FigmaGenerateTextCommand(Command):
    def __init__(self, css_text):
        super(FigmaGenerateTextCommand, self).__init__()
        self.css_text = "text { %s }" % (css_text)

    def run(self):
        result = "Text('')"
        dct = {}
        sheet = cssutils.parseString(self.css_text)
        for rule in sheet:
            styles = rule.style.cssText
            for property in rule.style:
                name = property.name
                value = property.value
                dct[name] = value
                # print("%s - %s" % (name, value))
                if name in CSS_METHOD:
                    try:
                        result += '\n    .{}'.format(
                            CSS_METHOD[name] % value.lower())
                    except TypeError as e:
                        value = value.lower().replace('px', '').replace('em', '')
                        if 'number is required' in str(e):
                            # int
                            result += '\n    .{}'.format(
                                CSS_METHOD[name] % int(value))
                        elif 'real number' in str(e):
                            # float
                            result += '\n    .{}'.format(
                                CSS_METHOD[name] % float(value))
        logResult(result)
