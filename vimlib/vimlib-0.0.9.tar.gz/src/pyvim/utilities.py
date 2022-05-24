""" General utilities for working with Python in Vim. """
from typing import Final


VimCommand = str  # Type Alias


def wrap_vim_command(
    command: str,
    silent: bool = False,
    clear: bool = True,
) -> VimCommand:
    """Wrap a Vim command with frequent strings.

    Allows easy chaining of Vim commands.

    Parameters
    ----------
    command : str
        The command to be wrapped.
    silent : bool, optional (default: False)
        Whether or not to suppress the output of the command.
    clear : bool, optional (default: True)
        Prepend <C-u> to the command: Clears the command line.

    Examples
    --------

    >>> # `:w` is the Vim command for writing the current buffer to disk.
    >>> print(wrap_vim_command('w'))
    :<C-u>w<CR>

    >>> print(wrap_vim_command('w!', silent=True))
    :<C-u>silent w!<CR>
    """

    enter: Final[str] = "<CR>"
    silent_prefix: Final[str] = "silent "

    if silent:
        command = silent_prefix + command

    if clear:
        # Needs to be first, so it doesn't clear other options.
        command = "<C-u>" + command

    command = ":" + command + enter

    return command
