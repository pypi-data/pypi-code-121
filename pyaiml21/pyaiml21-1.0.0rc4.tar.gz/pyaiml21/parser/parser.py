"""The AIML parser."""
from .logger import Logger
from ._xml_lxml_parser import LXMLParser as XMLParser
from ._category_parser import CategoryParser
from ._walker import Walker, TagSyntaxCheckerFn
from pyaiml21.ast import Category
from typing import Optional, List, Tuple, Dict


AIMLIF_SUBSTITUTIONS = {r"#\Newline": "\n", r"#\Comma": ","}


def _sub_aimlif(txt: str):
    for k, v in AIMLIF_SUBSTITUTIONS.items():
        txt = txt.replace(k, v)
    return txt


class AIMLParser:
    """
    Allows parsing XML files into tree-like objects.

    AIMLParser represents a parsing phase when loading AIML categories
    into the interpreter. Loads file, parses it as a XML file (ignoring
    all AIML syntax rules), and finds and returns the basic unit of knowledge,
    category elements, which are then validated.

    To enable the parser to validate other tags, use `add_tag` to pass
    the name of the tag and parsing function.

    Note: As category elements might be wrapped with <topic>, AIMLParser tries
    to correctly assign child node <topic> to all categories wrapped, i.e.

    .. code-block:: xml

            <topic name="...">
                <category>..</category>
            </topic>

    is transformed, internally, into

    .. code-block:: xml

            <category>
                ...
                <topic>topic_name</topic>
            </category>
    """

    def __init__(self):
        """Create empty parser without any AIML tags knowledge."""
        self.known_tags: Dict[str, TagSyntaxCheckerFn] = {}

    def add_tag(self, name: str, fn: TagSyntaxCheckerFn) -> None:
        """Enable the parser to correctly validate the <`name`> tag."""
        self.known_tags[name] = fn

    def _parse_aiml(self, source: str, is_file: bool) \
            -> Tuple[Optional[List[Category]], Logger]:
        """Parse .aiml file or text based on the `is_file` flag."""
        logger = Logger()
        root = XMLParser.parse(source, logger) \
            if is_file \
            else XMLParser.parse_text(source, logger)
        if not root or logger.has_errors():
            assert logger.has_errors()
            return None, logger
        categories = CategoryParser.get_categories(root, logger)
        for category in categories:
            Walker.walk(category, logger, self.known_tags)
        return categories, logger

    def parse_category_aiml(self, text: str) \
            -> Tuple[Optional[Category], Logger]:
        """
        Parse one <category> from the text.

        The only requirement is that <category> is the root element and
        text is well-formed xml document.

        :param text: string with <category> element
        :return: parsed category and the logger with reported errors,
            optionally the category might be None, in this case
            the logger contains at least one error
        """
        logger = Logger()
        # reuse the parser, create "AIML file" with one category
        text = f"<aiml>{text}</aiml>"
        root = XMLParser.parse_text(text, logger)
        if not root or logger.has_errors():
            assert logger.has_errors()
            return None, logger
        categories = CategoryParser.get_categories(root, logger)
        if not categories:
            return None, logger
        assert len(categories) == 1
        Walker.walk(categories[0], logger, self.known_tags)
        return categories[0], logger

    def parse_aiml_text(self, text: str)\
            -> Tuple[Optional[List[Category]], Logger]:
        """
        Parse AIML content from the `text`.

        The requirements on the text content are similar to the ones presented
        in the `parse_aiml_text` method.

        :param text: string with AIML content
        :return: list of categories and the logger with error messages;
            optionally the list of categories might be None, in this case
            the logger contains at least one error
        """
        return self._parse_aiml(text, is_file=False)

    def parse_aiml_file(self, filename: str)\
            -> Tuple[Optional[List[Category]], Logger]:
        """
        Parse .aiml file given by the `filename`.

        .aiml file is an XML file containing AIML elements, and <aiml>
        as the root element. Any syntactic errors are reported via the
        returned logger.

        :param filename: name of file to parse (.aiml)
        :return: list of categories and the logger with error messages;
            optionally the list of categories might be None, in this case
            the logger contains at least one error
        """
        return self._parse_aiml(filename, is_file=True)

    def parse_aimlif_file(self, filename: str)\
            -> Tuple[Optional[List[Category]], Logger]:
        """
        Parse .aimlif file given by the `filename`.

        The AIMLIF format is an alternative format to represent AIML files,
        where each category is stored on a single line. The elements
        are separated with a comma, in this order:

        activation count, pattern, that, topic, template, filename

        Notes:
            * this method completely ignores activation count as it does not
              seem to have any purpose;
            * the filename present on the line is also ignored;

        :param filename: .aimlif file to parse
        :return: list of categories and the logger with error messages;
            optionally the list of categories might be None, in this case
            the logger contains at least one error
        """
        logger = Logger()
        shadow_xml = []

        with open(filename, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f):
                if line.count(",") != 5:
                    logger.error_xml_syntax("AIMLIF: expected five commas",
                                            filename, lineno)
                    return None, logger

                _, pat, tha, top, tem, _ = map(_sub_aimlif, line.split(","))
                category_children = []

                for text, tag in zip([pat, tem, tha, top],
                                     ["pattern", "template", "that", "topic"]):
                    tagged_text = f"<{tag}>{text}</{tag}>"
                    category_children.append(tagged_text)

                cat_inner = "".join(category_children)
                cat = f"<category>{cat_inner}</category>"
                shadow_xml.append(cat)

        return self.parse_aiml_text("<aiml>" + "".join(shadow_xml) + "</aiml>")
