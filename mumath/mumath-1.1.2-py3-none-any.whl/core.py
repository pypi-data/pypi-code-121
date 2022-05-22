from .glyph import Glyph
from .lex import Lexer
from .grammar import MathParser
from .node.writer import tostring

# inspired by
# https://github.com/Python-Markdown/markdown/blob/master/markdown/core.py
# https://github.com/pygments/pygments/blob/master/pygments/__init__.py


class MuMath:
    def __init__(self, glyph, lexer, parser):
        self.glyph = glyph
        self.lexer = lexer
        self.parser = parser

    @classmethod
    def from_area(cls, area, **options):
        glyph = Glyph.from_area(area)
        lexer = Lexer.from_glyph(glyph)
        parser = MathParser(glyph, **options)

        return cls(glyph, lexer, parser)

    def convert(self, source):
        tree = self.build(source)
        html = tostring(tree.getroot())
        return html

    def convert_file(self, file, output=None, encoding=None):
        encoding = "utf-8" if encoding is None else encoding

        with open(file, mode="r", encoding=encoding) as f:
            html = self.convert(f.read())

        if output is not None:
            with open(output, mode="w", encoding=encoding) as f:
                f.write(html)
        else:
            print(html)

        return self

    def build(self, source, root=None):
        tokens = list(self.lexer.tokenize(source))
        return self.parser.parse(tokens, root)
