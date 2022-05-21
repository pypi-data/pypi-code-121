"""Tree-walking interpreter."""
from typing import Callable, Dict, List
from pyaiml21.ast import Node
from pyaiml21.bot import Bot
from pyaiml21.graphmaster import StarBindings
from pyaiml21.session import Session
from .symbol_table import SymbolTable


AIMLEvalFun = Callable[['Interpreter', Node], str]


_DEFAULT_ANSWER = "default"


class Interpreter:
    """
    A tree-walking interpreter used to evaluate the AIML <template> tags.

    Recursively evaluate the bot's reply, by using defined evaluation rules
    given in `known_tags`. To update these, feel free to use method `register`.

    A new interpreter instance should be created for each user-chatbot
    message.

    If there is no answer found for the given input, the interpreter
    returns the value of bot's _predicate "default".
    """

    def __init__(self, bot: Bot, session: Session):
        """
        Create an AIML interpreter.

        :param bot: the chatbot that needs to be interpreted
        :param session: the chatbot-user session with the user for whom
            we wish to evaluate the bot's reply
        """
        self.bot = bot
        self.session = session
        self.known_tags: Dict[str, AIMLEvalFun] = {}
        self._stars_stack: List[StarBindings] = []
        self._variables_stack: List[SymbolTable] = []
        self._failing: bool = False  # should we interrupt the execution?
        self._fail_msg = ""  # the result when we fail
        self.recursion_limit = 100

    def _get_default_reply(self):
        return self.bot.get_property(_DEFAULT_ANSWER)

    @property
    def stars(self) -> StarBindings:
        """Access stars for current category."""
        assert len(self._stars_stack)
        return self._stars_stack[-1]

    @property
    def vars(self) -> SymbolTable:
        """Access local variables for current category."""
        assert len(self._variables_stack)
        return self._variables_stack[-1]

    def eval_seq(self, seq: List[Node]) -> str:
        """Evaluate a sequence of nodes, concatenating the results."""
        return "".join(filter(None, map(self.eval, seq)))  # filter non-empty

    def eval_unknown(self, node: Node) -> str:
        """Evaluate unknown tag by keeping the xml in the result."""
        return node.to_xml(self.eval)

    def eval(self, node: Node) -> str:
        """
        Evaluate `node` and return the result.

        Use `self.known_tags` to find the proper evaluation function.

        :param node: AST node to be evaluated
        :return: evaluated string
        """
        self.enter(node)

        if node.is_text_node:
            assert node.text
            self.leave(node, node.text)
            return node.text

        assert node.tag is not None
        fn = self.known_tags.get(node.tag)
        if fn is not None:
            result = fn(self, node)
        else:
            result = self.eval_unknown(node)

        self.leave(node, result)
        return result

    def add_frame(self, _pattern: str, stars: StarBindings):
        """Add stack frame for current <template>."""
        self._stars_stack.append(stars)
        self._variables_stack.append(SymbolTable())

    def pop_frame(self):
        """Pop stack frame when leaving current <template>."""
        self._stars_stack.pop()
        self._variables_stack.pop()

    def _call(self, fn: str, node: Node, stars: StarBindings) -> str:
        """Push + eval + pop."""
        assert node.tag == "template"
        self.add_frame(fn, stars)
        if len(self._variables_stack) >= self.recursion_limit:
            self.fail("Recursion limit exceeded.")
        result = self.eval_seq(node.children)
        result = " ".join(result.split())
        self.pop_frame()
        return result

    def call(self, input_: str) -> str:
        """Find the response for the input given by `input_`."""
        if self._failing:
            return self._fail_msg

        # as even <srai> might contain a multi-sentence query, we need
        # to evaluate each sentence separately
        sentences = self.bot.preprocess(input_)
        user = self.session.user_id
        answers = []
        for s in sentences:
            searched = self.bot.search_brain(user, s)
            if searched is None:
                answers.append(self._get_default_reply())
                continue
            node, stars, _ = searched
            result = self._call(s, node, stars)
            answers.append(result)

        if self._failing:
            answers = [self._fail_msg]  # type: ignore

        # if we have empty stack, reset self._failing
        if not self._variables_stack:
            self._failing = False
            self._fail_msg = ""
        return " ".join(answers)

    def register(self, tag: str, fn: AIMLEvalFun):
        """Register a function used to interpret AIML, possibly overriding."""
        self.known_tags[tag] = fn

    def fail(self, result: str = ""):
        """Interrupt the evaluation of the response, returning `result`."""
        self._failing = True
        self._fail_msg = result or self._get_default_reply()

    def fail_node(self, node: Node) -> str:
        """
        Announce the interpreter that evaluation of `node` failed.

        During evaluation, this method is called whenever an assertion
        should fail (index is not decimal, e.g.). To resolve the situation,
        it first tries to call {tag}FAILED, if not successful, the interpreter
        returns predefined constant.
        """
        # first try to call node.tag + FAILED
        assert node.tag
        search_string = f"{node.tag.upper()}FAILED"
        matched = self.bot.search_brain(self.session.user_id, search_string)
        if matched is None or not matched[2]:
            self.fail(self._get_default_reply())  # AIML 1.0.1 - return unknown
            # noinspection PyUnreachableCode
            return ""
        root, stars, _ = matched
        return self._call(search_string, root, stars)

    def enter(self, _node: Node):
        """Call when starting the evaluation of `node`."""
        pass

    def leave(self, _node: Node, _result: str):
        """Call when the evaluation of `node` finished with `result`."""
        pass
