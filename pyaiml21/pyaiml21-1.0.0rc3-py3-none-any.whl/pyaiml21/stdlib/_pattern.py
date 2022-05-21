from typing import List

from pyaiml21.aiml import AIMLVersion
from pyaiml21.ast import Node
from pyaiml21.graphmaster import GraphMaster, GMNode, Pattern, MatchFn
from pyaiml21.parser import Logger

# symbols used in graphmaster when <bot> or <set> node is found: ...
__SET__ = "__SET__"
__BOT__ = "__BOT__"


###############################################################################
# Utilities
###############################################################################

def _allows_attr_children(node: Node):
    if node.aiml_version is None:
        return True  # if we dont know version, assume it is allowed
    return node.aiml_version >= AIMLVersion.V2_0


def _expect_text_log(text):
    def _parse_node(node: Node, _logger: Logger):
        return _expect_text(text)(node)

    return _parse_node


def _expect_attribute(node: Node, attr: str, logger: Logger):
    found_attr = attr in node.attributes
    found_child = False
    if _allows_attr_children(node):
        for child in node.children:
            if child.tag == attr or found_attr:
                if found_child:
                    logger.error_duplicate_element(child)
                found_child = True
    if not (found_attr or found_child):
        logger.error_missing_attr(node, attr)


def _expect_text(text):
    def _rec_node(node: Node) -> bool:
        return node.is_text_node and node.text == text

    return _rec_node


def _adv_text_match(gm_node: GMNode, node: Node) -> GMNode:
    assert node.text is not None
    return gm_node.children[node.text]


###############################################################################
# <bot>
###############################################################################

def _parse_bot(node: Node, logger: Logger):
    if not _recognise_bot(node):
        return False
    _expect_attribute(node, "name", logger)
    for child in node.children:
        if child.is_text_node:
            logger.error(child, "unexpected text element")
        elif child.tag != "name":
            logger.warn_unexpected_element(child)
        else:
            assert child.tag == "name"
            if len(node.children) != 1 or not child.children[0].is_text_node:
                logger.error(child, "<bot>: name should be a text")
            else:
                name = child.children[0]
                assert name.text
                if " " in name.text:
                    logger.warning(name, "<name> should be a single word")
    return True


def _recognise_bot(node: Node):
    return node.tag == "bot"


def _advance_bot(gm_node: GMNode, node: Node):
    prop = node.attributes.get("name") or node.children[0].children[0]
    assert prop and prop.text
    return gm_node.children[__BOT__].children[prop.text.upper()]


def _match_bot(seq, pos, node: GMNode, gm: GraphMaster):
    if __BOT__ not in node.children:
        return
    # "<bot name> is equivalent to A word"
    bot_node = node.children[__BOT__]
    properties = gm.bot_config.properties
    for prop_name in bot_node.children.keys():
        if prop_name in properties and seq[pos] == properties[prop_name]:
            yield bot_node.children[prop_name], 1


###############################################################################
# <set>
###############################################################################

def _parse_set(node: Node, logger: Logger):
    if node.tag != "set":
        return False
    if len(node.children) != 1:
        logger.error(node, "set should have only one child")
    elif node.children[0].text is None:
        logger.error(node.children[0], "expecting set name")
    elif " " in node.children[0].text:
        logger.error(node.children[0], "name of set should be one word")
    return True


def _recognise_set(node: Node):
    return node.tag == "set"


def _advance_set(gm_node: GMNode, node: Node) -> GMNode:
    set_name = node.children[0].text
    assert set_name is not None
    return gm_node.children[__SET__].children[set_name]


def _match_set(seq, pos, node: GMNode, gm: GraphMaster):
    if __SET__ not in node.children:
        return
    all_sets = node.children[__SET__]
    sought = ""  # phrase we are seeking
    for i in range(pos, len(seq)):
        if sought:
            sought += " "
        sought += seq[i]
        for set_name, next_node in all_sets.children.items():
            set_exists = set_name in gm.bot_config.sets
            if set_exists and sought in gm.bot_config.sets[set_name]:
                yield next_node, i - pos + 1


###############################################################################
# words
###############################################################################

def _parse_word(priority: bool):
    def _parse_word_(node: Node, logger: Logger):
        version = node.aiml_version
        if priority and version and version < AIMLVersion.V2_0:
            logger.warning(node, "priority matching was defined in AIML 2.0")
        return _recognise_word(priority)(node)

    return _parse_word_


def _recognise_word(priority: bool):
    def _rec(node: Node):
        if not node.is_text_node:
            return False
        assert node.text is not None
        return (not priority) or node.text.startswith("$")

    return _rec


def _match_word(priority: bool):
    """
    Decorate a function to match (priority) word.

    :param priority: if True, the decorated function matched only priority
        word, if False, only exact match is done
    """
    def _match(seq, pos, node: GMNode, _gm: GraphMaster):
        word = f"${seq[pos]}" if priority else seq[pos]
        if word in node.children:
            yield node.children[word], 1

    return _match


###############################################################################
# stars
###############################################################################

def _parse_star(symbol: str, min_version: AIMLVersion):
    """
    Decorate function to parse any wildcard symbol.

    :param symbol: the form of the wildcard
    :param min_version: first version this wildcard was defined
    :return: function that parses this wildcard
    """

    def _parse(node: Node, logger: Logger):
        assert node.text == symbol
        if node.aiml_version and node.aiml_version < min_version:
            logger.warning(node, f"'{symbol}' not defined in this version")
            return False
        return True

    return _parse


def _match_star(symbol: str, min_words: int) -> MatchFn:
    """
    Decorate function to match the star.

    :param symbol: the form of the star wildcard
    :param min_words: minimum number of words this wildcard matches
    :return: function that matched this wildcard
    """

    def _match(seq: List[str], pos: int, node: GMNode, _gm: GraphMaster):
        if symbol not in node.children:
            return None
        next_node = node.children[symbol]
        for i in range(min_words, len(seq) + 2 - pos):
            yield next_node, i

    return _match


###############################################################################
# exports
###############################################################################


EXACT_MATCH_SCORE = 100  # for failing nodes and calling {tag}FAILED


_PRIORITY_WORD = Pattern(EXACT_MATCH_SCORE, False,
                         _parse_word(True),
                         _recognise_word(True),
                         _adv_text_match,
                         _match_word(True))

_STAR_SHARP = Pattern(50, True,
                      _parse_star("#", AIMLVersion.V2_0),
                      _expect_text("#"),
                      _adv_text_match, _match_star("#", 0))

_STAR_UNDERSCORE = Pattern(40, True,
                           _parse_star("_", AIMLVersion.V1_0),
                           _expect_text("_"),
                           _adv_text_match, _match_star("_", 1))

_PLAIN_WORD = Pattern(30, False, _parse_word(False), _recognise_word(False),
                      _adv_text_match, _match_word(False))

_BOT_PROPERTY = Pattern(30, False, _parse_bot, _recognise_bot, _advance_bot,
                        _match_bot)

_PATTERN_SET = Pattern(20, True, _parse_set, _recognise_set, _advance_set,
                       _match_set)

_STAR_CARET = Pattern(10, True,
                      _parse_star("^", AIMLVersion.V2_0),
                      _expect_text("^"),
                      _adv_text_match, _match_star("^", 0))

_STAR_ASTERISK = Pattern(0, True,
                         _parse_star("*", AIMLVersion.V1_0),
                         _expect_text("*"),
                         _adv_text_match, _match_star("*", 1))

PATTERNS: List[Pattern] = [
    _PRIORITY_WORD,
    _STAR_SHARP,
    _STAR_UNDERSCORE,
    _PLAIN_WORD,
    _BOT_PROPERTY,
    _PATTERN_SET,
    _STAR_CARET,
    _STAR_ASTERISK
]

__all__ = ["PATTERNS", "EXACT_MATCH_SCORE"]
