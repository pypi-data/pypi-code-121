from rich.console import Console

_console = None


def get_console():
    global _console
    if _console is None:
        _console = Console(force_terminal=True, force_interactive=True)
    return _console


def print(*objects):
    _console = get_console()
    _console.print(*objects)
