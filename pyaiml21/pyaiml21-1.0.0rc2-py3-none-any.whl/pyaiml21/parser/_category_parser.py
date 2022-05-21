from typing import Iterable, List, Optional

from pyaiml21.ast import Node, Category
from .logger import Logger


class CategoryParser:
    """
    Extract categories from the parsed XML tree.

    Extracting categories is the second phase of the parser, where
    the AIML syntax errors might be discovered, hence each method
    has parameter `logger` to report the errors.
    """

    @staticmethod
    def _parse_topic(node: Node, logger: Logger) -> Iterable[Category]:
        """
        Parse <topic> returning an all its categories.

        Note that only direct descendants of <aiml> should be parsed as `node`
        parameter to this function. For parsing <topic> as a child of category,
        referer to `_parse_category`.

        :param node: XML node in the form <topic name="topic_name">
        :param logger: logger to store the data about errors into
        :returns: iterable of categories found within this topic
        """
        topic_name = node.attributes.get("name")
        if topic_name is None:
            logger.error_missing_attr(node, "name")
            return

        for child in node.children:
            if child.text is not None and not child.text.strip():
                continue
            if child.is_text_node:
                logger.warn_unexpected_element(child)
                continue
            if child.tag != "category":
                logger.error(child, "expected <category> element (as a child "
                                    "of <topic> element)")
                continue
            c = CategoryParser._parse_category(child, logger, topic_name.text)
            if c is not None:
                yield c

    @staticmethod
    def _parse_category(
            node: Node,
            logger: Logger,
            topic_name: Optional[str] = None
    ) -> Optional[Category]:
        """
        Parse <category> node and return the intermediate representation.

        Note that we do not require the explicit pattern-that-topic-template
        order of <category>'s children.

        :param node: <category> node
        :param logger: logger to store errors and warnings into
        :param topic_name: topic to use (in case <topic><category/></topic>)
        :returns: parsed ``Category``
        """
        assert node.tag == "category"
        elems = {}  # sub-element of category
        for child in node.children:
            if child.is_text_node:
                logger.warn_unexpected_element(child)
                continue
            if child.tag in elems:
                logger.error(child, f"Duplicate <{child.tag}> tag")
            elems[child.tag] = child

        # make sure the category contains necessary sub-tags
        # (pattern, template) and at most (pattern, that, topic, template)
        minimal = {"pattern", "template"}
        maximal = minimal.union({"that", "topic"})
        found = elems.keys()

        for x in minimal:
            if x not in found:
                logger.error(node, f"Missing element: {x}")
        for f in found:
            if f not in maximal:
                logger.error(node, f"Unexpected category element: {f}")

        topic = None
        if topic_name is not None:
            topic = Node.Element("topic", node, filename=node.filename)
            topic_text = Node.Value(topic_name, topic, node.filename)
            topic.children = [topic_text]

        # finally, if this element is within <topic> and it itself contains
        # <topic>, issue a warning
        if topic is not None and "topic" in elems:
            logger.warning(node,
                           "duplicate topic, child of <category> will be used")

        if logger.has_errors():
            return None

        return Category(
            elems["pattern"],
            elems["template"],
            elems.get("that", None),
            elems.get("topic", topic)
        )

    @staticmethod
    def get_categories(root: Node, logger: Logger) -> List[Category]:
        """
        Given <aiml> root, find and return all <category> elements.

        :param root: <aiml> root element
        :param logger: logger to report errors to
        :returns: list of all aiml categories found
        """
        result = []
        assert not root.is_text_node
        for child in root.children:
            if child.text is not None and not child.text.strip():
                continue
            if child.is_text_node:
                logger.warn_unexpected_element(child)
            elif child.tag == "category":
                cat = CategoryParser._parse_category(child, logger)
                if cat is not None:
                    result.append(cat)
            elif child.tag == "topic":
                cats = CategoryParser._parse_topic(child, logger)
                result.extend(cats)
        return result
