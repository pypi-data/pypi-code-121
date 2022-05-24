""" Vim mappings for Python. """
from enum import auto
from enum import Flag
from typing import Union

try:
    import vim
except ImportError:
    pass


class SpecialArgument(Flag):
    """Special arguments for mappings.

    `:help :map-arguments` for more information.

    `:map <OPTION1> <OPTION2> ... <OPTIONN> ,w :do-something<CR>`
    """

    BUFFER = auto()
    NOWAIT = auto()
    SILENT = auto()
    SCRIPT = auto()
    EXPR = auto()
    UNIQUE = auto()

    def __init__(self, value: int):
        # self._name_ is Optional[str]
        if self._name_ is not None:
            self._name_ = self._name_.lower()
        else:
            self._name_

    def __str__(self):
        included_options: list[SpecialArgument] = [
            flag for flag in SpecialArgument if flag & self
        ]
        return " ".join(f"<{flag._name_}>" for flag in included_options)


def get_mapping(mapping: str, key: str, command: str) -> str:
    """Get a mapping.

    Examples
    --------
    >>> print(set_mapping('nmap', '<Leader>r', ':<C-u>silent w'))
    nmap <Leader>r :silent w

    """
    raise NotImplementedError("`get_mapping` is not implemented yet.")


def set_mapping(
    mapping: str,
    key: str,
    command: str,
    special_arguments: Union[SpecialArgument, str] = "",
) -> None:
    """Set a mapping.

    Examples
    --------
    >>> # Set <Leader>r to write current buffer to disk.
    >>> # Equivalent to `:nmap <Leader>r :<C-u>silent w<CR>` in Vim.
    >>> set_mapping('nmap', '<Leader>r', ':<C-u>silent w<CR>')
    """
    vim_command: str = "{} {} {} {}".format(
        mapping, special_arguments, key, command
    )

    vim.command(vim_command)
    return None
