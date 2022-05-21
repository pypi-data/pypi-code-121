"""
Simple interactive AIML debugger.

This module contains a definition of an (interactive) debugger for
evaluating AIML <template>. The debugger is capable of debugging
only a single AIML category -- not the graphmaster. To run it, use

.. code-block:: py

    d = Debugger(my_bot, my_session)
    d.known_tags = my_bot.eval_tags
    d.set_break("some_file.aiml", 15)
    d.call("PREPROCESSED INPUT")

To get help and see available commands, use `.help()` method or
":h" or ":help" in the interactive session.

Note that without setting any breakpoints prior running the debugger
immediately evaluates the response and returns.

It should also be noted, that the debugger works the same as the
interpreter with regards to the recursive calls, so if the
evaluation of the <aiml> caused RecursionError, the evaluation
in debugger will cause it as well as long as no breakpoints
are specified and the execution is stopped.
"""
from .walker import Interpreter
from pyaiml21.bot import Bot
from pyaiml21.session import Session
from typing import List, Callable, Optional, Set, Any
from pyaiml21.ast import Node
from dataclasses import dataclass
from pathlib import Path


@dataclass
class _DOption:
    """Helper class to represent Debugger options."""

    f: Callable[..., Any]  # function to call when option is activated
    help: str              # option description
    cmds: List[str]        # list of possible commands to activate the option


class Debugger(Interpreter):
    """
    Interactive AIML debugger.

    This is built on top of the interpreter and allows simple
    debugging of AIML source code.
    """

    PROMPT = "(debug) "

    def __init__(self, bot: Bot, session: Session):
        """
        Create a debugger.

        :param bot: bot which configuration should be debugged
        :param session: the current bot-user session (for local graphmaster),
            should be one of the sessions of the bot
        """
        super().__init__(bot, session)
        self.breakpoints: Set[str] = set()    # filename:line
        self.trace: List[str] = []            # stack of activated functions
        self._stop_condition = lambda: False  # should we interrupt execution?
        self._node_stack: List[Node] = []
        self.return_value: Optional[str] = None  # last return value
        self.next_stack_size_stop: int = -1  # for `next`

        self.options = [
            _DOption(self.help, "Print help.", [":h", ":help"]),
            _DOption(self.where, "Print stack trace.", [":w", ":where"]),
            _DOption(self.position, "Print current location.", [":pos"]),
            _DOption(self.set_break, "Set breakpoint file line", [":bp"]),
            _DOption(self.view_bps, "View Breakpoints", [":bps"]),
            _DOption(self.remove_bp, "Remove breakpoint (use same value as "
                                     "in `:bps`", [":rm"]),
            _DOption(self.step, "Make one evaluation step", [":s", ":step"]),
            _DOption(self.next, "Step into", [":n", ":next"]),
            _DOption(self.cont, "Continue evaluation", [":c", ":cont"]),
            _DOption(
                self.p,
                "Print value of _predicate (p name "
                "{predicate_name}) or variable (p var {variable_name}) "
                "or last return value",
                [":p"]
            ),
            _DOption(self.quit, "Quit debugging", [":q"])
        ]
        self.options_f = {x: o.f for o in self.options for x in o.cmds}

    def stop_on_first(self):
        """Pause the evaluation on the first interpreted node."""
        self._stop_condition = lambda: True

    @property
    def node(self) -> Optional[Node]:
        """Return the node that is currently being evaluated."""
        if not self._node_stack:
            return None
        return self._node_stack[-1]

    def view_bps(self) -> None:
        """Display set breakpoints."""
        print("Breakpoints:")
        for bp in self.breakpoints:
            print("\t", bp)

    def remove_bp(self, bp: str) -> None:
        """Remove chosen breakpoint."""
        bp = bp.strip()
        if bp not in self.breakpoints:
            print("No breakpoint:", bp)
        self.breakpoints.remove(bp)

    def call(self, input_: str) -> str:
        """Update the stacktrace with `input_`."""
        self.trace.append(input_)
        res = super().call(input_)
        self.trace.pop()
        return res

    def interact(self):
        """Run the interactive loop, expecting commands from CLI."""
        keep_interacting = True
        while keep_interacting and not self._failing:
            line = input(self.PROMPT)
            cmd, *args = line.split()
            if not cmd.startswith(":"):
                print(self.PROMPT, "debugger commands should start with ':'")
                self.help()
            elif cmd in [":bp"]:
                if len(args) != 2:
                    print(self.PROMPT, "wrong argument, enter `file line`")
                    continue
                file, line = args
                self.set_break(file, line)
            elif cmd in [":p"]:
                if not args:
                    self.p(None, None)
                else:
                    self.p(args[0], args[1])
            elif cmd in [":rm"]:
                if len(args) != 1:
                    print(self.PROMPT, "expected 1 argument")
                else:
                    self.remove_bp(args[0])
            elif cmd not in self.options_f:
                print(self.PROMPT, "invalid command")
            else:
                self.options_f[cmd]()
            if cmd in (":q", ":s", ":step", ":n", ":next", ":c", ":cont"):
                break

    def help(self):
        """Print help."""
        print("Debugger options help:")
        options_names = [", ".join(opt.cmds) for opt in self.options]
        max_offset = max(map(len, options_names))
        for arg, opt in zip(options_names, self.options):
            print(f"\t{arg.ljust(max_offset)}\t{opt.help}")
        print()

    def _bp(self, filename, line):
        name = Path(filename).name
        return f"{name}:{line}"

    def where(self):
        """Print stack trace."""
        print("Categories:")
        for t in self.trace:
            print("\t", t)
        print("\nNodes:")
        for n in self._node_stack:
            print("\t", n.to_xml(lambda _: ""))

    def position(self):
        """Print position of the node being evaluated."""
        assert self.node is not None
        node_desc = self.node.to_xml(lambda _: "")
        print(self.node.filename, self.node.line, node_desc)

    def set_break(self, filename, line):
        """Set a breakpoint on the file `filename` on line `line`."""
        self.breakpoints.add(self._bp(filename, line))

    def step(self):
        """Make one evaluation step, possibly using recursive <srai>."""
        self._stop_condition = lambda: True

    def next(self):
        """Make one eval step within this function (not stopping in <srai>)."""
        self.next_stack_size_stop = len(self._node_stack)
        self._stop_condition = lambda: (
            self.next_stack_size_stop == len(self._node_stack)
        )

    def cont(self):
        """Continue evaluation."""
        assert self.node is not None
        self._stop_condition = lambda: False

    def p(self, type_, name):
        """Return the value of a _predicate or a variable, or return value."""
        if type_ is None:
            print(self.return_value)
        elif type_ == "name":
            print(self.session.predicates.get(name))
        else:
            print(self.vars.get(name))

    def stop(self):
        """Interrupt execution."""
        # since we are running the debugger and the interpreter in the same
        # python loop, to stop, we just request another command
        self.interact()

    def quit(self):
        """Quit debugging session."""
        self.fail("[End Debugging]")
        # noinspection PyUnreachableCode
        self.cont()

    def _check_stop(self, node: Node):
        bpoint_name = self._bp(node.filename, node.line)
        if self._stop_condition() or bpoint_name in self.breakpoints:
            self._stop_condition = lambda: False
            self.stop()  # yield, raise or interactive commands, or thread

    def enter(self, node: Node):
        """Start the evaluation of `node`."""
        self._node_stack.append(node)
        self._check_stop(node)

    def leave(self, _node: Node, result: str):
        """End the evaluation of `_node`, update stacks."""
        self.return_value = result
        assert self._node_stack, "Expected non-empty node-stack."
        self._node_stack.pop()
        if self.node:
            self._check_stop(self.node)
