import markdown
import re
import xml.etree.ElementTree as ET
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
from .util import peek, pop
from .glyph import Glyph
from .lex import Lexer
from .grammar import MathParser


def _parse_attributes(attributes):
    pattern = r"""
        (?P<attrib>[\w:!.#-]+)           # Attribute
        (?:\s*=\s*                       # Value assignment
            (?:[\'"](?P<quoted>.*)[\'"]  # Quoted value
            |(?P<unquoted>\S*))          # Unquoted value
        )?                               # Value is optional
    """

    matches = re.finditer(pattern, attributes, re.VERBOSE)

    for m in matches:
        if m.lastgroup == "attrib":
            yield (m["attrib"], None)
        elif m.lastgroup == "quoted":
            yield (m["attrib"], m["quoted"])
        elif m.lastgroup == "unquoted":
            yield (m["attrib"], m["unquoted"])


def _alias_attributes(attributes):
    LANG_ALIAS = {
        "py": "python3",
        "js": "javascript",
        "chem": "chemistry",
    }

    ATT_ALIAS = {
        "#": "linenos",
        "!": "hl_lines",
        "@": "lineanchors",
    }

    # first attribute is positional language parameter
    (att, val), attributes = peek(attributes, default=("#", None))
    if not att.startswith("#") and val is None:
        pop(attributes)
        yield ("area", LANG_ALIAS.get(att, att))

    for att, val in attributes:
        yield (ATT_ALIAS.get(att, att), val)


def _options(attributes):
    option_keys = {
        "area", "wrap", "linenos", "linenostart", "hl_lines",
        "lineanchor", "multiline", "numbering", "align",
        "display", "counter",
    }

    options = {}
    attribs = {}
    for att, val in attributes:
        (options if att in option_keys else attribs)[att] = val

    if "linenos" in options:
        counter = options.pop("linenos")
        options["counter"] = True if counter is None else int(counter)

    return options, attribs


def options_attributes(attributes):
    return _options(_alias_attributes(_parse_attributes(attributes)))


class MuMathProcessor(BlockProcessor):
    RE_FENCE_START = r'^ *(\${2,})'
    RE_FENCE_END = r''

    def test(self, parent, block):
        return re.match(self.RE_FENCE_START, block)

    def _capture_content(self, blocks):
        start_block = blocks[0]

        m = self.test(None, blocks[0])
        blocks[0] = start_block[m.end(0):]

        fence = re.escape(m.group(1))
        for i, block in enumerate(blocks):
            if n := re.search(fence, block):
                end_block = blocks[i]
                before, after = end_block[:n.start(0)], end_block[n.end(0):]

                # This reverts the blocking
                content = "\n\n".join(blocks[0:i+1])

                blocks[i] = after

                remove_end = i + int(after.isspace())
                del blocks[:remove_end]
                return content

        # Undo (order is important)
        blocks[0] = start_block

        return None

    def run(self, parent, blocks):
        content = self._capture_content(blocks)

        if content is None:
            return False

        if content.startswith("\\"):
            # since $$\begin{align} is common
            # though \begin{align} isn't really supported
            options = ""
        else:
            options, _, content = content.partition("\n")

        options, attributes = options_attributes(options)

        glyph = Glyph.from_area(options.pop("area", None))
        lexer = Lexer.from_glyph(glyph)
        parser = MathParser(glyph, align=True, **options)

        tokens = list(lexer.tokenize(content))
        root = parser.parse(tokens).getroot()
        root.attrib.update(attributes)

        parent.append(root)


class InlineMuMathProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        content = m.group(1)

        if content.startswith("("):
            # this leaves the first ( intact
            # but it is ignored in the parser
            options, _, content = content.partition(")")
        else:
            options = ""
        options, attributes = options_attributes(options)

        glyph = Glyph.from_area(options.pop("area", None))
        lexer = Lexer.from_glyph(glyph)
        parser = MathParser(glyph, align=False, **options)

        tokens = list(lexer.tokenize(content))
        root = parser.parse(tokens).getroot()
        root.attrib.update(attributes)

        return root, m.start(0), m.end(0)


class InlineMuMark(Extension):
    config = {
        "priority": [110, "Extension priority"],
    }

    def extendMarkdown(self, md):
        MATH_PATTERN = r"\$(.*?)\$"
        md.inlinePatterns.register(
            InlineMuMathProcessor(MATH_PATTERN, md), "mumath-inline", 110)


class MuMark(Extension):
    config = {
        "priority": [110, "Extension priority"],
    }

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            MuMathProcessor(md.parser), "mumath", self.getConfig("priority", 110))
