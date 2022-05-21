import glob
from functools import wraps
from typing import Dict, Callable, List, Optional, Set
import subprocess
import js2py
import random

from pyaiml21.ast import Node
from pyaiml21.aiml import AIMLVersion
from pyaiml21.botconfig import Substitutions
from pyaiml21.interpreter import AIMLEvalFun, Interpreter
from pyaiml21.parser import Logger, TagSyntaxCheckerFn as ParseFn
from pyaiml21._version import __version__

from ._time import read_cformat, read_jformat, extract_diff, format_now
from ._sraix import sraix_pandorabots


TEMPLATE_PARSER: Dict[str, ParseFn] = {}
TEMPLATE_EVAL: Dict[str, AIMLEvalFun] = {}

# for <loop/>
MAX_LOOP_COUNT = 1000


###############################################################################
# decorators
###############################################################################

def parses(tag: str):
    """Add defined function to `TEMPLATE_PARSER` functions."""
    tag_name = tag.lstrip("<").rstrip(">")

    def decorator(f: ParseFn):
        @wraps(f)
        def wrapper(node: Node, logger: Logger) -> None:
            assert node.tag == tag_name
            f(node, logger)
        TEMPLATE_PARSER[tag_name] = wrapper
        return wrapper
    return decorator


def evals(tag: str):
    """Add defined function to `TEMPLATE_EVAL` functions."""
    tag_name = tag.lstrip("<").rstrip(">")

    def decorator(f: AIMLEvalFun):
        @wraps(f)
        def wrapper(interpreter, node: Node) -> str:
            assert node.tag == tag_name
            return f(interpreter, node)
        TEMPLATE_EVAL[tag_name] = wrapper
        return wrapper
    return decorator


###############################################################################
# misc
###############################################################################


def _check_version(
    node: Node,
    logger: Logger,
    min_version: Optional[AIMLVersion] = None,
    max_version: Optional[AIMLVersion] = None
):
    """
    Parse the version attribute of AST node.

    Verify that the AIML construct represented by `node` has version in
    the given range and report with a warning. If any of the versions
    is `None`, given check is skipped.
    """
    version = node.aiml_version
    if version is None:
        return
    if min_version is not None and version < min_version:
        logger.warn_not_defined(node, min_version)
    if max_version is not None and max_version < version:
        logger.warn_deprecated(node, max_version)


def _optional_attr(
    attr: str,
    node: Node,
    logger: Logger,
    default_value: Optional[str] = None
) -> None:
    """
    Find the attribute `attr` in the node.

    If it is not found, use  default value if present,
    if multiple occurrences are found log it as a duplicate error.

    Then normalize node (putting the attribute to `node.attributes`)
    """
    has_attr = attr in node.attributes
    child_attr = None

    # check children: if any of them have the required attribute, store
    # the child for later, if you find multiple, this is duplicate attribute
    # which is an error
    for child in node.children:
        if child.tag == attr:
            if child_attr is not None or has_attr:
                logger.error_duplicate_element(child)
            child_attr = child

    if child_attr is not None:
        # if we found a child with the attribute, assuming we have not found
        # an XML attribute, we put it into the node's attributes and remove
        # it from children, the condition will be checked later
        node.attributes[attr] = child_attr
        node.children.remove(child_attr)
    elif (default_value is not None) and (not has_attr):
        # if we did not find a child and neither the XML attribute
        # and we have a default value, set it
        node.attributes[attr] = Node.Value(default_value, node)
        return

    # if we are version less than 2.0 and attribute was found among
    # children, we fire a warning (interpreter can recover from this, but
    # the user should know that this is not ok)
    child_attr_allowed = (
        node.aiml_version is None or node.aiml_version >= AIMLVersion.V2_0
    )
    if not child_attr_allowed and not has_attr and (child_attr is not None):
        logger.warning(node, "specifying attributes as children as allowed "
                             f"since {AIMLVersion.V2_0.value}, but current "
                             f"version is {node.aiml_version}")


def _expect_attr(attr: str, node: Node, logger: Logger) -> None:
    """
    Find the attribute `attr` in the node.

    If it is not found, log it, if multiple occurrences are found log it.
    Then normalize node (putting the attribute to `node.attributes`).

    Used for the required (non-empty) attributes.
    """
    _optional_attr(attr, node, logger, None)
    if attr not in node.attributes:
        logger.error_missing_attr(node, attr)


def _no_children_except(node: Node, logger: Logger, allowed: Set[str]):
    """
    Parse a node with children.

    Check that `node` has no other children than those with tags
    in `allowed`. Does not check the duplicity of children tags.

    This also checks the text children of the node, to enable them,
    pass `None` to the `allowed` attributes.
    """
    for child in node.children:
        if child.tag not in allowed and child.text != " ":
            logger.error_unexpected_element(child)


def _map_str(walker: Interpreter, node: Node, f: Callable[[str], str])\
        -> str:
    """Apply `f` to the result obtained by evaluating `node`'s children."""
    return f(walker.eval_seq(node.children))


def _has_var_xor_name(node: Node, logger: Logger):
    """Check that `node` has exactly one of the attributes 'var' and 'name'."""
    VAR, NAME = "var", "name"
    var = VAR in node.attributes or any(c.tag == VAR for c in node.children)
    attr = VAR if var else NAME
    _expect_attr(attr, node, logger)


def _add_default_star_child(node: Node) -> Node:
    """
    Add <star index="1"/> as a child to childless `node`.

    A few elements allow short-hand notation
        <tag/>
    while the semantics is of
        <tag><star index="1"/></tag>

    This function transforms the former the the equivalent form.
    """
    if not node.children:
        star = Node.Element("star", node)
        index = Node.Value("1", star)
        star.attributes["index"] = index
        node.children = [star]
    return node


def _eval_attr(walker: Interpreter, node: Node, attr: str) -> str:
    """Evaluate the `node`'s attribute `attr`."""
    assert attr in node.attributes
    attr_node = node.attributes[attr]
    if not attr_node.is_text_node:
        return walker.eval_seq(attr_node.children)
    assert attr_node.text is not None
    return attr_node.text


###############################################################################
# (chat) history
###############################################################################


@parses("<that>")
def _parse_that(node: Node, logger: Logger):
    _optional_attr("index", node, logger, "1,1")
    _no_children_except(node, logger, {"index"})

    # finally, if index was already present as an XML attribute,
    # we can immediately check whether it has the correct form
    if "index" in node.attributes and node.is_text_node:
        txt = node.attributes["index"].text
        assert txt is not None
        if txt.count(",") != 1:
            logger.error(node, "wrong format of attribute index "
                               f"(expected one comma), found {txt}")
        else:
            left, right = txt.split(",")
            if not left.isdecimal() or not right.isdecimal():
                logger.error(node, "index of that should be represented "
                                   f"by two numbers, but was {left} and "
                                   f"{right}")


@evals("<that>")
def _eval_that(walker: Interpreter, node: Node) -> str:
    index = _eval_attr(walker, node, "index")
    if index.count(",") != 1:
        return walker.fail_node(node)
    response, sentence = index.split(",")
    if not (response.isdecimal() and sentence.isdecimal()):
        return walker.fail_node(node)
    res, sen = int(response) - 1, int(sentence) - 1
    reply = walker.session.get_bot_reply(res)
    if sen >= len(reply):
        return walker.fail_node(node)
    return reply[-sen - 1]


###############################################################################


@parses("<input>")
def _parse_input(node: Node, logger: Logger):
    _optional_attr("index", node, logger, "1")
    _no_children_except(node, logger, {"index"})


@evals("<input>")
def _eval_input(walker: Interpreter, node: Node) -> str:
    index = _eval_attr(walker, node, "index")
    if not index.isdecimal() or int(index) <= 0:
        return walker.fail_node(node)

    i = int(index) - 1
    request_idx = 0
    query = walker.session.get_user_query(request_idx)
    while i >= len(query):
        i -= len(query)

        # if the history is not unbounded and we arrive at the end,
        # we fail - see `session.get_user_query` for details
        if not query:
            return walker.fail_node(node)

        request_idx += 1
        query = walker.session.get_user_query(request_idx)
    return walker.session.get_user_query(request_idx)[-i - 1]  # from the back


###############################################################################


@parses("<response>")
def _parse_response(node, logger):
    _check_version(node, logger, AIMLVersion.V2_0)
    _optional_attr("index", node, logger, "1")
    _no_children_except(node, logger, {"index"})


@evals("<response>")
def _eval_response(walker: Interpreter, node: Node) -> str:
    index = _eval_attr(walker, node, "index")
    if not index.isdecimal():
        return walker.fail_node(node)

    reply = walker.session.get_bot_reply(int(index) - 1)
    # similar to <input> if there was no reply (bounded list or just
    # not enough interactions happened), we fail
    if not reply:
        walker.fail_node(node)

    return " ".join(reply)


###############################################################################


@parses("<request>")
def _parse_req(node, logger):
    _check_version(node, logger, AIMLVersion.V2_0)
    _optional_attr("index", node, logger, "1")
    _no_children_except(node, logger, {"index"})


@evals("<request>")
def _eval_request(walker: Interpreter, node: Node) -> str:
    index = _eval_attr(walker, node, "index")
    if not index.isdecimal():
        walker.fail_node(node)
    # similar to <response>
    response = walker.session.get_user_query(int(index) - 1)
    if not response:
        return walker.fail_node(node)
    return " ".join(response)


###############################################################################
# other systems
###############################################################################


@parses("<system>")
def _parse_sys(node: Node, logger: Logger):
    """
    Parse <system> tag.

    <system> has no syntax requirements, however to prevent
    stalling, we defined XML attribute timeout to be number of
    seconds to let the process run before killing it and failing
    """
    if "timeout" in node.attributes:
        assert node.attributes["timeout"].text
        if not node.attributes["timeout"].text.isdecimal():
            logger.error(node, "timeout should be integer")


@evals("<system>")
def _eval_sys(walker: Interpreter, node: Node) -> str:
    command = walker.eval_seq(node.children)
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    timeout = None
    if "timeout" in node.attributes:
        # it was an XML attribute
        assert node.attributes["timeout"].text is not None
        timeout = float(node.attributes["timeout"].text)
    process.wait(timeout=timeout)
    result = []
    if not process.stdout:
        return walker.fail_node(node)
    from pathlib import Path
    print(Path(".").absolute())
    print(command)
    for line in process.stdout.readlines():
        byte_string = line.decode("utf-8")
        result.append(byte_string.strip())
    print(result)
    resolved = " ".join(result)
    return resolved


###############################################################################


@parses("<javascript>")
def _parse_js(_node: Node, _logger: Logger):
    # no requirements are laid on javascript
    return


@evals("<javascript>")
def _eval_js(walker: Interpreter, node: Node) -> str:
    js_code = walker.eval_seq(node.children)
    return str(js2py.eval_js(js_code))


###############################################################################
# control flow
###############################################################################


@parses("<think>")
def _parse_think(_node: Node, _logger: Logger):
    # nothing to do
    pass


@evals("<think>")
def eval_think(walker: Interpreter, node: Node) -> str:
    walker.eval_seq(node.children)
    return ""

###############################################################################


@parses("<if>")
def _parse_if(node: Node, logger: Logger):
    """
    Parse <if> tag.

    <if> was defined only in AIML 1.0 and was then replaced with more
    general <condition> tag, for backwards compatibility, we will
    support it.

    <if> has mandatory child <then> and optional <else>. The attributes
    of <if> are name - the name of the _predicate and value
    """
    _check_version(node, logger, max_version=AIMLVersion.V1_0)
    _expect_attr("name", node, logger)
    _expect_attr("value", node, logger)
    EXPECTED_CHILDREN = ("then", "else")
    found_children: Set[str] = set()

    for child in node.children:
        if child.is_text_node or child.tag not in EXPECTED_CHILDREN:
            logger.error_unexpected_element(child)
        elif child.tag in found_children:
            logger.error_duplicate_element(child)
        else:
            found_children.add(child.tag)


@parses("<then>")
def _parse_then(node: Node, logger: Logger):
    """
    Parse <then> tag.

    <then> has no attributes, no other requirements but that <if> is its
    parent
    """
    _check_version(node, logger, max_version=AIMLVersion.V1_0)
    if not node.parent or node.parent.tag != "if":
        logger.error(node, "<then> must be a child of <if>")


@parses("<else>")
def _parse_else(node: Node, logger: Logger):
    """
    Parse AIML 1.0 <else> tag.

    <else> has no attributes, no other requirements but that <if> is its
    parent
    """
    _check_version(node, logger, max_version=AIMLVersion.V1_0)
    if not node.parent or node.parent.tag != "if":
        logger.error(node, "<else> must be a child of <if>")


@evals("<if>")
def _eval_if(walker: Interpreter, node: Node) -> str:
    name = _eval_attr(walker, node, "name")
    value = _eval_attr(walker, node, "value")
    real_value = walker.bot.get_predicate(name, walker.session.user_id)
    searched_child = "then" if real_value == value else "else"
    for child in node.children:
        if child.tag == searched_child:
            return walker.eval_seq(child.children)
    return ""


###############################################################################


@parses("<loop>")
def _parses_loop(node: Node, logger: Logger):
    _check_version(node, logger, AIMLVersion.V2_0)
    _no_children_except(node, logger, set())
    assert node.parent
    node.parent.attributes["loop"] = node


@evals("<loop>")
def _eval_loop(*_args, **_kwargs):
    return ""


@parses("<li>")
def _parses_li(*_args, **_kwargs):
    """
    Parse <li> tag.

    This is a dummy function not to trigger any eval warning.
    """


def _parse_condition_1(node: Node, logger: Logger):
    """
    Parse <condition> of 1st type.

    First condition, convert from:
        <condition name=... value=...>text
    to:
        <condition>
            <li name=... value=...>text
    """
    _expect_attr("value", node, logger)
    _has_var_xor_name(node, logger)

    attr = "name" if "name" in node.attributes else "var"
    attr_node = node.attributes[attr]
    value = node.attributes["value"]
    li = Node.Element("li", node, {attr: attr_node, "value": value})
    attr_node.parent = li
    value.parent = li
    node.attributes.pop(attr, None)
    node.attributes.pop("value", None)
    li.children = node.children
    node.children = [li]
    for child in node.children:
        child.parent = li


def _parse_condition_2(node: Node, logger: Logger):
    """
    Parse <condition> of 2nd type.

    Second condition - converting from:
        <condition name=..>
            <li value=...>

    to:
        <condition>
            <li name=... value=...>
    """
    _has_var_xor_name(node, logger)
    _no_children_except(node, logger, {"li"})
    attr = "name" if "name" in node.attributes else "var"

    # now all children must be li elements
    is_last_li = True
    for child in reversed(node.children):
        if not child.tag == "li":
            logger.error_unexpected_element(child)
            continue
        if is_last_li:
            _optional_attr("value", child, logger)
        else:
            _expect_attr("value", child, logger)
        is_last_li = False
        child.attributes[attr] = node.attributes[attr]


def _parse_condition_3(node: Node, logger: Logger):
    """Parse <condition> of 3rd type."""
    is_last_li = True
    if "name" in node.attributes or "var" in node.attributes:
        logger.error(node, "unexpected attributes")
    for child in reversed(node.children):
        if not child.tag == "li":
            logger.error_unexpected_element(child)
            continue
        if is_last_li:
            _optional_attr("value", child, logger)
            if "value" in child.attributes:
                _has_var_xor_name(child, logger)
        else:
            _expect_attr("value", child, logger)
            _has_var_xor_name(child, logger)
        is_last_li = True


@parses("<condition>")
def _parses_condition(node: Node, logger: Logger):
    """
    Parse the <condition> tag.

    <condition> has three forms, to distinguish between them
    we do the following
        1) no <li> children -> 1st type
        2) var/name in attribs or children -> 2nd type
        3) else 3rd type
    each form will be converted to the (3)-rd type to make the evaluation
    step easier
    """
    if not any(child.tag == "li" for child in node.children):
        _parse_condition_1(node, logger)
    elif any(child.tag in ("var", "name") for child in node.children)\
            or any(attr in node.attributes for attr in ("var", "name")):
        _parse_condition_2(node, logger)
    else:
        _parse_condition_3(node, logger)
    # finally remove space characters
    node.children = [c for c in node.children if not c.is_text_node]


def _condition_li_satisfies(walker: Interpreter, li_node: Node) -> bool:
    BOUND = "*"
    assert li_node.tag == "li"
    if "value" not in li_node.attributes:
        return True  # default <li></li>

    # found value of _predicate/variable
    value = _eval_attr(walker, li_node, "value")
    real_val: Optional[str]  # real value of _predicate/variable

    if "name" in li_node.attributes:
        name = _eval_attr(walker, li_node, "name")
        # to correctly handle default predicates and bound names,
        # we need to aquire different things here...
        if value == BOUND:
            real_val = walker.session.predicates.get(name)
        else:
            real_val = walker.bot.get_predicate(name, walker.session.user_id)
    else:
        assert "var" in li_node.attributes
        var = _eval_attr(walker, li_node, "var")
        real_val = walker.vars.get(var)
    return (real_val == value) or (value == BOUND and real_val is not None)


@evals("<condition>")
def eval_condition(walker: Interpreter, node: Node) -> str:
    current_loop_count = 0
    result: List[str] = []
    continue_flag = True

    while current_loop_count < MAX_LOOP_COUNT and continue_flag:
        continue_flag = False  # have we found <loop/> ?
        for child in node.children:
            if _condition_li_satisfies(walker, child):
                if "loop" in child.attributes:
                    continue_flag = True
                res = walker.eval_seq(child.children)
                result.append(res)
                break
        if continue_flag:
            current_loop_count += 1

    if not continue_flag:
        return "".join(result)
    # else the loop count is higher than MAX_LOOP_COUNT, we fail
    return walker.fail_node(node)


###############################################################################


@parses("<random>")
def _parses_random(node: Node, logger: Logger):
    """
    Parse <random> tag.

    <random> has no requirements on the AIML version, the only requirement
    is that all its children are <li> elements
    """
    for child in node.children:
        _no_children_except(node, logger, {"li"})
    # ignore spacing here
    node.children = [c for c in node.children if not c.is_text_node]


@evals("<random>")
def _eval_random(walker: Interpreter, node: Node) -> str:
    li = random.choice(node.children)
    return walker.eval_seq(li.children)


###############################################################################
# srai(x)
###############################################################################

@parses("<sraix>")
def _parse_sraix(node: Node, logger: Logger):
    """
    Parse <sraix> tag.

    <sraix> can have multiple attributes: bot, limit, service, apikey, botid,
    server, hint, default

    We, however, only support Pandorabots (mostly because pannous is
    inaccessible), so the validated tags are as follows:

    * botid - required
    * bot - ignored
    * limit - optional (default value 3)
    * service - ignored
    * apikey - ignored
    * server - ignored
    * hint - ignored
    * default - optional

    Ignored attributes, however, are moved away from children array
    """
    _check_version(node, logger, AIMLVersion.V2_0)
    _expect_attr("botid", node, logger)
    _optional_attr("limit", node, logger, "3")
    _optional_attr("default", node, logger)
    for attr in ("bot", "service", "apikey", "server", "hint"):
        _optional_attr(attr, node, logger)


@evals("<sraix>")
def eval_sraix(walker: Interpreter, node: Node) -> str:
    input_ = walker.eval_seq(node.children)
    botid = _eval_attr(walker, node, "botid")
    limit = _eval_attr(walker, node, "limit")
    if not limit.isdecimal():
        return walker.fail_node(node)

    response = sraix_pandorabots(botid, input_)
    if response is not None:
        return " ".join(response[:int(limit)])
    if "default" in node.attributes:
        return _eval_attr(walker, node, "default")
    return walker.fail_node(node)


###############################################################################


@parses("<sr>")
def _parses_sr(node: Node, logger: Logger):
    """
    Parse <sr/> tag.

    The <sr/> element is equivalent to <srai><star index="1"/></srai>
    so we just check it has no children and transform it (this changed
    the AST) to the equivalent form.
    """
    _no_children_except(node, logger, set())
    node.tag = "srai"
    _add_default_star_child(node)


###############################################################################


@parses("<srai>")
def _parses_srai(*_args, **_kwargs):
    # nothing to do
    pass


@evals("<srai>")
def eval_srai(walker: Interpreter, node: Node) -> str:
    fn_name = walker.eval_seq(node.children)
    return walker.call(fn_name)


###############################################################################
# learning
###############################################################################


def _eval_learn_rec(walker: Interpreter, node: Node) -> str:
    """Evaluate <learn(f)>, by ignoring everything till <eval> is found."""
    if node.tag == "eval":
        return walker.eval_seq(node.children)
    return node.to_xml(lambda n: _eval_learn_rec(walker, n))


@parses("<eval>")
def _parses_eval(node: Node, logger: Logger):
    # the only condition for eval is that somewhere up the tree, there is
    # <learn> or <learnf> tag
    node_: Optional[Node] = node
    while node_ is not None:
        if node_.tag == "learn" or node_.tag == "learnf":
            return
        node_ = node_.parent
    logger.error(node, "<eval> must be a child of <learn> or <learnf>")


@parses("<learn>")
def _parses_learn(*_args, **_kwargs):
    # check has category element? does not have to! <star/>
    pass


@evals("<learn>")
def _eval_learn(walker: Interpreter, node: Node) -> str:
    data = "".join(_eval_learn_rec(walker, x) for x in node.children)
    if node.aiml_version is not None and node.aiml_version < AIMLVersion.V2_0:
        for file in map(str, glob.glob(data)):
            # silently fail here, the primary learning mechanism is via
            # bot methods
            walker.bot.learn_aiml(file)
    else:
        walker.bot.learn_category(
            data,
            global_=False,
            user_id=walker.session.user_id
        )
    return ""


###############################################################################


@parses("<learnf>")
def _parses_learnf(node: Node, logger: Logger):
    # check has category element? does not have to! <star/>
    _check_version(node, logger, min_version=AIMLVersion.V2_0)


@evals("<learnf>")
def _eval_learnf(walker: Interpreter, node: Node) -> str:
    category = "".join(_eval_learn_rec(walker, n) for n in node.children)
    walker.bot.learn_category(
        category,
        global_=True,
        user_id=walker.session.user_id
    )
    return ""


###############################################################################


@parses("<gossip>")
def _parses_gossip(*_args, **_kwargs):
    # nothing to do
    pass


@evals("<gossip>")
def _eval_gossip(walker: Interpreter, node: Node) -> str:
    gossip = walker.eval_seq(node.children)
    filename = walker.bot.config.gossip_filename
    if filename is not None:
        # (a+) to append or create
        with open(filename, "a+", encoding="utf-8") as f:
            f.write("\n" + gossip + "\n")
    return ""


###############################################################################
# substitutions
###############################################################################


def _sub(walker: Interpreter, node: Node, subs: Substitutions) -> str:
    text = walker.eval_seq(node.children)
    return subs.sub(text)


@parses("<map>")
def _parses_map(node: Node, logger: Logger):
    # need to distinguish from oob map and normal map, simply by checking
    # whether this map has a name and letting oob map pass through
    _check_version(node, logger, AIMLVersion.V2_0)
    name_node: Optional[Node] = None
    has_attr = "name" in node.attributes

    for child in node.children:
        if child.tag == "name":
            if name_node is not None or has_attr:
                logger.error_duplicate_element(child)
            name_node = child

    if name_node is None:
        if not has_attr:
            logger.error_missing_attr(node, "name")
        return
    if not has_attr:
        node.attributes["name"] = name_node
        name_node.parent = node
        node.children.remove(name_node)


@evals("<map>")
def _eval_map(walker: Interpreter, node: Node) -> str:
    if "name" not in node.attributes:
        # probably oob map
        return walker.eval_unknown(node)
    text = walker.eval_seq(node.children)
    # for successful matching and consistency, convert to uppercase
    # as values in the map are in upper case (see also ProgramAB)
    text = text.upper()
    # eval <name> element
    map_name = _eval_attr(walker, node, "name")
    if map_name not in walker.bot.config.maps:
        return walker.fail_node(node)
    return walker.bot.config.maps[map_name].get(text) or walker.fail_node(node)


###############################################################################


def _parse_substitution(node: Node, logger: Logger) -> None:
    """
    Parse a substitution node.

    Each of the real-substitution tags has also a shortened form,
    e.g

        `<person/> === <person><star index="1"/></person>`

    so we transform the node (changing its children) to
    the equivalent form.

    If it has any children, this transformation does nothing.

    However the grammar does not allow this, it is only mentioned
    in the text specification - in order to be consistent, we allow
    this form for each substitution, while issuing warnings.
    """
    # the case only happens when node has no children
    if not node.children:
        from_ = f"<{node.tag}/>"
        to_ = f"<{node.tag}><star index='1'/></{node.tag}>"
        logger.weak_warning(node, f"non-standard conversion from "
                                  f"\"{from_}\" to \"{to_}\"")
        _add_default_star_child(node)


@parses("<person>")
def _parses_person(node: Node, logger: Logger):
    _parse_substitution(node, logger)


@evals("<person>")
def _eval_person(walker: Interpreter, node: Node) -> str:
    return _sub(walker, node, walker.bot.config.person)


###############################################################################


@parses("<person2>")
def _parses_person2(node: Node, logger: Logger):
    _parse_substitution(node, logger)


@evals("<person2>")
def _eval_person2(walker: Interpreter, node: Node) -> str:
    return _sub(walker, node, walker.bot.config.person2)


###############################################################################


@parses("<gender>")
def _parses_gender(node: Node, logger: Logger):
    _parse_substitution(node, logger)


@evals("<gender>")
def _eval_gender(walker: Interpreter, node: Node) -> str:
    return _sub(walker, node, walker.bot.config.gender)


###############################################################################


@parses("<normalize>")
def _parses_norm(node: Node, logger: Logger):
    _parse_substitution(node, logger)


@evals("<normalize>")
def _eval_norm(walker: Interpreter, node: Node) -> str:
    return _sub(walker, node, walker.bot.config.normalize)


###############################################################################


@parses("<denormalize>")
def _parses_denorm(node: Node, logger: Logger):
    _check_version(node, logger, min_version=AIMLVersion.V2_0)
    _parse_substitution(node, logger)


@evals("<denormalize>")
def _eval_denorm(walker: Interpreter, node: Node) -> str:
    return _sub(walker, node, walker.bot.config.denormalize)


###############################################################################
# stars
###############################################################################


def _eval_starexpr(walker: Interpreter, node: Node, stars: List[str])\
        -> str:
    index = _eval_attr(walker, node, "index")
    if not index.isdecimal():
        return walker.fail_node(node)
    idx = int(index) - 1  # indexing from 1
    if idx < 0 or idx >= len(stars):
        return walker.fail_node(node)  # unknown index
    return stars[idx]


@parses("<star>")
def _parse_star(node: Node, logger: Logger):
    _optional_attr("index", node, logger, "1")
    _no_children_except(node, logger, {"index"})


@evals("<star>")
def _eval_star(walker: Interpreter, node: Node) -> str:
    return _eval_starexpr(walker, node, walker.stars.stars)


###############################################################################


@parses("<thatstar>")
def _parse_thatstar(node: Node, logger: Logger):
    _optional_attr("index", node, logger, "1")
    _no_children_except(node, logger, {"index"})


@evals("<thatstar>")
def _eval_thatstar(walker: Interpreter, node: Node) -> str:
    return _eval_starexpr(walker, node, walker.stars.thatstars)


###############################################################################


@parses("<topicstar>")
def _parse_topicstar(node: Node, logger: Logger):
    _optional_attr("index", node, logger, "1")
    _no_children_except(node, logger, {"index"})


@evals("<topicstar>")
def _eval_topicstar(walker: Interpreter, node: Node) -> str:
    return _eval_starexpr(walker, node, walker.stars.topicstars)


###############################################################################
# string processing
###############################################################################


@parses("<lowercase>")
def _parses_lcase(*_args, **_kwargs):
    # nothing to do
    pass


@evals("<lowercase>")
def _eval_lcase(walker: Interpreter, node: Node) -> str:
    return _map_str(walker, node, str.lower)

###############################################################################


@parses("<uppercase>")
def _parses_ucase(*_args, **_kwargs):
    # nothing to do
    pass


@evals("<uppercase>")
def _eval_ucase(walker: Interpreter, node: Node) -> str:
    return _map_str(walker, node, str.upper)

###############################################################################


@parses("<formal>")
def _parses_formal(*_args, **_kwargs):
    # nothing to do
    pass


@evals("<formal>")
def _eval_formal(walker: Interpreter, node: Node) -> str:
    return _map_str(walker, node, str.title)

###############################################################################


@parses("<sentence>")
def _parses_sentence(*_args, **_kwargs):
    # nothing to do
    pass


@evals("<sentence>")
def _eval_sentence(walker: Interpreter, node: Node) -> str:
    return _map_str(walker, node, str.capitalize)

###############################################################################


@parses("<explode>")
def _parses_explode(node: Node, logger: Logger):
    _check_version(node, logger, AIMLVersion.V2_0)


def explode_string(s: str) -> str:
    return " ".join(filter(str.isprintable, s))


@evals("<explode>")
def _eval_explode(walker: Interpreter, node: Node) -> str:
    return _map_str(walker, node, explode_string)


###############################################################################
# date
###############################################################################


@parses("<date>")
def _parse_date(node: Node, logger: Logger):
    _optional_attr("locale", node, logger)
    _optional_attr("timezone", node, logger, "0")
    _optional_attr("format", node, logger)
    _optional_attr("jformat", node, logger)
    if "format" in node.attributes and "jformat" in node.attributes:
        logger.error(node, "duplicate format specified")
    _no_children_except(node, logger, {"locale", "format", "jformat"})
    # if there is no format, we return whatever is the easiest
    if "format" not in node.attributes and "jformat" not in node.attributes:
        node.attributes["format"] = Node.Value("%Y-%M-%D %H:%M:%S")


@evals("<date>")
def _eval_date(walker: Interpreter, node: Node) -> str:
    locale_ = tz = format_ = jformat = None
    if "locale" in node.attributes:
        locale_ = _eval_attr(walker, node, "locale")
    if "timezone" in node.attributes:
        tz = _eval_attr(walker, node, "timezone")
    if "format" in node.attributes:
        format_ = _eval_attr(walker, node, "format")
    if "jformat" in node.attributes:
        jformat = _eval_attr(walker, node, "jformat")
    return format_now(locale_, tz, format_, jformat) or walker.fail_node(node)


###############################################################################


@parses("<interval>")
def _parse_interval(node: Node, logger: Logger):
    _expect_attr("from", node, logger)
    _expect_attr("to", node, logger)
    _expect_attr("style", node, logger)
    _optional_attr("format", node, logger)
    _optional_attr("jformat", node, logger)
    has_jformat = "jformat" in node.attributes
    has_cformat = "format" in node.attributes
    if has_cformat and has_jformat:
        logger.error(node, "expected one of: <jformat>, <format>, found both")
    elif not (has_cformat or has_jformat):
        logger.error(node, "missing formatting attribute jformat or format")


@evals("<interval>")
def _eval_interval(walker: Interpreter, node: Node) -> str:
    from_ = _eval_attr(walker, node, "from")
    to_ = _eval_attr(walker, node, "to")

    if "jformat" in node.attributes:
        jformat = _eval_attr(walker, node, "jformat")
        from_dt = read_jformat(from_, jformat)
        to_dt = read_jformat(to_, jformat)
    else:
        assert "format" in node.attributes
        cformat = _eval_attr(walker, node, "format")
        from_dt = read_cformat(from_, cformat)
        to_dt = read_cformat(to_, cformat)

    if from_dt is None or to_dt is None:
        return walker.fail_node(node)

    diff = to_dt - from_dt
    style = _eval_attr(walker, node, "style")
    return extract_diff(diff, style) or walker.fail_node(node)


###############################################################################
# variables
###############################################################################


def _which_var(walker: Interpreter, node: Node):
    if "name" in node.attributes:
        return "name", walker.session.predicates
    return "var", walker.vars


###############################################################################


@parses("<set>")
def _parse_set(node: Node, logger: Logger):
    _has_var_xor_name(node, logger)
    if "var" in node.attributes:
        _check_version(node, logger, AIMLVersion.V2_0)
    # set might have empty children
    if not node.children:
        logger.warning(node, "setting value to empty string")


@evals("<set>")
def _eval_set(walker: Interpreter, node: Node) -> str:
    type_, vars_ = _which_var(walker, node)
    name = _eval_attr(walker, node, type_)
    value = walker.eval_seq(node.children)
    vars_[name] = value
    return ""


###############################################################################


@parses("<get>")
def _parse_get(node: Node, logger: Logger):
    _has_var_xor_name(node, logger)
    if "var" in node.attributes:
        _check_version(node, logger, AIMLVersion.V2_0)


@evals("<get>")
def _eval_get(walker: Interpreter, node: Node) -> str:
    type_, _ = _which_var(walker, node)
    name = _eval_attr(walker, node, type_)
    if type_ == "var":
        return walker.vars.get(name) or walker.fail_node(node)
    return walker.bot.get_predicate(name, walker.session.user_id)


###############################################################################


@parses("<bot>")
def _parse_bot(node: Node, logger: Logger):
    _expect_attr("name", node, logger)
    _no_children_except(node, logger, {"name"})


@evals("<bot>")
def _eval_bot(walker: Interpreter, node: Node) -> str:
    name = _eval_attr(walker, node, "name")
    return walker.bot.get_property(name)


###############################################################################
# misc
###############################################################################


@parses("<version>")
def _parse_vs(node: Node, logger: Logger):
    _no_children_except(node, logger, set())


@evals("<version>")
def _eval_vs(_walker: Interpreter, _node) -> str:
    return f"{__version__}"


###############################################################################


@parses("<program>")
def _parse_program(node: Node, logger: Logger):
    _no_children_except(node, logger, set())


@evals("<program>")
def _eval_program(_walker: Interpreter, _node) -> str:
    return f"Interpreter pyaiml21, version {__version__}"

###############################################################################


@parses("<size>")
def _parse_sz(node: Node, logger: Logger):
    _no_children_except(node, logger, set())


@evals("<size>")
def _eval_sz(walker: Interpreter, _node: Node) -> str:
    return str(walker.bot.brain_size(walker.session.user_id))


###############################################################################


@parses("<id>")
def _parse_id(node: Node, logger: Logger):
    _no_children_except(node, logger, set())


@evals("<id>")
def _eval_id(walker: Interpreter, _node: Node) -> str:
    return walker.session.user_id


###############################################################################


@parses("<vocabulary>")
def _parse_voc(node: Node, logger: Logger):
    _no_children_except(node, logger, set())


@evals("<vocabulary>")
def _eval_voc(walker: Interpreter, _node: Node) -> str:
    return str(walker.bot.vocabulary(walker.session.user_id))


###############################################################################
# -exports
###############################################################################


__all__ = ["TEMPLATE_EVAL", "TEMPLATE_PARSER"]
