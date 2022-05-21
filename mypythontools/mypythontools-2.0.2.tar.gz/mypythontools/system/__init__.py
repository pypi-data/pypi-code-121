"""Add some stuff to python subprocess, sys, os and platform libraries.

You can find here formatting errors, resolving venv script paths, finding script path, unifying syntax for
linux and windows etc. Most used function is 'terminal_do_command' comunicating with system shell. 
Use strings as input and if there can be space in some command, use 'get_console_str_with_quotes'.
"""
from mypythontools.system.system_internal import (
    check_library_is_available,
    check_script_is_available,
    get_console_str_with_quotes,
    is_wsl,
    PYTHON,
    SHELL_AND,
    terminal_do_command,
    which,
)

__all__ = [
    "check_library_is_available",
    "check_script_is_available",
    "get_console_str_with_quotes",
    "is_wsl",
    "PYTHON",
    "SHELL_AND",
    "terminal_do_command",
    "which",
]
