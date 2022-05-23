"""
Model for a pseudo-switch/case statement based around context-managers.

Use as follows:

with switch(value):
    if case(option1):
        ...
        break_()
    if case(option2):
        ...
        break_()
    if case(option3):
        ...
    if case(option4):
        ... falls through ...
        break_()
    if case(option5,
            option6,
            option7):
        ... multi-case ...
        break_()
    if default():
        ...
        break_()

"""
import threading
from typing import List, Dict

# The context-stack for each thread, so we can work out which
# switch statement the case function should work with
context_stacks: Dict[int, List['SwitchContextManager']] = dict()

# The thread lock for the context stacks
thread_lock: threading.RLock = threading.RLock()


def get_context_stack() -> List['SwitchContextManager']:
    """
    Makes sure the switch context-manager stack is initialised for this thread.

    :return:    The stack.
    """
    # Get the thread we're running on
    current_thread: int = threading.get_ident()

    with thread_lock:
        # Ensure there is a context stack for that thread
        if current_thread not in context_stacks:
            context_stacks[current_thread] = []

        # Return the stack
        return context_stacks[current_thread]


def add_to_stack(context_manager: 'SwitchContextManager'):
    """
    Adds a new SwitchContextManager to the thread stack.

    :param context_manager:     The new switch context manager.
    """
    # Put ourselves on the stack
    get_context_stack().append(context_manager)


def pop_from_stack():
    """
    Removes the top switch context manager from the thread stack.
    """
    # Get the context stack
    stack = get_context_stack()

    # Make sure it's not empty
    if len(stack) == 0:
        raise SwitchError("Attempted to remove switch context-manager from empty stack")

    # Pop the top of the stack
    stack.pop()


def get_current_context_manager() -> 'SwitchContextManager':
    """
    Gets the current switch context manager for this thread.

    :return:    The SwitchContextManager.
    """
    # Get the stack for this thread
    stack = get_context_stack()

    # Make sure it's not empty
    if len(stack) == 0:
        raise SwitchError("No switch context-manager for this thread")

    # Peek the top of the stack
    return stack[-1]


class SwitchContextManager:
    """
    Context manager for switch-case blocks.
    """
    def __init__(self, on):
        self.on = on
        self.matched: bool = False
        self.executed_default: bool = False

    def __enter__(self):
        # Add ourselves as the current context manager for the thread
        add_to_stack(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Remove ourselves as the current context manager for the thread
        pop_from_stack()

        # If a break statement was used to exit,
        # don't propagate the exception
        return exc_type is BreakSwitchException

    def case(self, first_case, *cases) -> bool:
        # Check we haven't already executed default
        self.check_default_executed()

        # If we match any of the provided cases, always match from now on
        if self.on in (first_case, *cases):
            self.matched = True

        # Allows for fall-through
        return self.matched

    def default(self) -> bool:
        # Check we haven't already executed default
        self.check_default_executed()

        # Flag that we've executed the default statement
        self.executed_default = True

        # Execute the default block if nothing has matched yet
        return not self.matched

    def check_default_executed(self):
        # If we've already executed default, automatically break
        if self.executed_default:
            break_()


def switch(on) -> SwitchContextManager:
    """
    Sugar method for setting up the switch-case context manager.

    :param on:  The value to be switched on.
    :return:    The switch context manager.
    """
    return SwitchContextManager(on)


def case(first_case, *cases) -> bool:
    """
    Sugar method which checks if any of the given cases matches
    the switch statement.

    :param first_case:  The first value to match.
    :param cases:       Any additional values to match.
    :return:            True if matched, False if not.
    """
    # Get the current context
    current_context: SwitchContextManager = get_current_context_manager()

    # Call it to check the cases provided
    return current_context.case(first_case, *cases)


def default():
    """
    Special version of the case statement which only matches
    if no previous case statements did. Automatically breaks.

    :return:    True if no case statement has matched,
                False otherwise.
    """
    # Get the current context
    current_context: SwitchContextManager = get_current_context_manager()

    # Check if we should execute the default block
    return current_context.default()


def break_():
    """
    Breaks from the switch block.
    """
    raise BreakSwitchException()


class BreakSwitchException(Exception):
    """
    A special exception that is thrown and caught by the switch context-manager
    to break from a switch block.
    """
    pass


class SwitchError(Exception):
    """
    Class for errors using the switch statement.
    """
    pass
