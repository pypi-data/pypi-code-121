import os
from typing import Optional

from colorama import Fore, Back, Style

from .cursor import Cursor
from .getchar import getchar


class Terminal:
    """Main terminarty class."""
    _instance = None
    _updating_line = ''

    INPUT_STYLE = f'{Fore.YELLOW} > {Style.RESET_ALL}'

    def __init__(self) -> None:
        if Terminal._instance is not None:
            raise RuntimeError('Only one instance of Terminal is allowed')
        Terminal._instance = self

    @staticmethod
    def clear() -> None:
        """Clears entire terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def bell() -> None:
        """Makes an audible noise."""
        print('\a', end='')

    @staticmethod
    def save_screen() -> None:
        """Save current terminal screen state. Can be restored with ``Terminal.restore_screen()``."""
        print('\033[?47h', end='')

    @staticmethod
    def restore_screen() -> None:
        """Restores current terminal screen state. Can be saved with ``Terminal.save_screen()``."""
        print('\033[?47l', end='')

    @staticmethod
    def input(text: str) -> str:
        """Gets input from the user. Just like built in ``input()`` function just with more style."""
        Terminal.clear()
        print(text)
        inp = input(Terminal.INPUT_STYLE)
        Terminal.clear()
        return inp

    @staticmethod
    def getchar() -> bytes:
        """Gets one character from the user input."""
        return getchar()

    @staticmethod
    def print(*args, sep: Optional[str] = ' ') -> None:
        """Used for printing text, when progress bar or waiting is running."""
        if Terminal._updating_line:
            s = '\r' + sep.join(list(map(str, args)))
            print(s, end=f'{" " * (len(Terminal._updating_line) - len(s))}\n')
            print(Terminal._updating_line, end='')
        else:
            print(*args, sep=sep)

    @staticmethod
    def choise(text: str, choices: list[str], *, index: bool = False) -> str:
        inp = 0
        while not isinstance(inp, int) or inp < 1 or inp > len(choices):
            Terminal.clear()
            print(text)
            for i, c in enumerate(choices):
                print(f'{Fore.RED}[{Fore.YELLOW}{i + 1}{Fore.RED}]{Style.RESET_ALL} {c}')
            try:
                print(Terminal.INPUT_STYLE, end='')
                inp = int(Terminal.getchar())
            except ValueError:
                pass
        Terminal.clear()
        return inp - 1 if index else choices[inp - 1]

    @staticmethod
    def select(text: str, choices: list[str], *, index: bool = False) -> str:
        selected = 0
        Terminal.clear()
        Cursor.up(len(text.splitlines()) + len(choices) + 1)
        while True:
            print(text)
            for i, choise in enumerate(choices):
                print(f'{Back.LIGHTBLACK_EX if i == selected else Back.BLACK}',
                      f'{choise}',
                      f'{Style.RESET_ALL}',
                      sep='')
            char1 = Terminal.getchar()
            if char1 == b'\r':
                break
            elif char1 != b'\xe0':
                Cursor.up(len(text.splitlines()) + len(choices) + 1)
                continue
            char2 = Terminal.getchar()
            if char2 == b'H':
                selected -= 1
                if selected < 0:
                    selected = len(choices) - 1
            elif char2 == b'P':
                selected += 1
                if selected == len(choices):
                    selected = 0
            Cursor.up(len(text.splitlines()) + len(choices) + 1)
        Terminal.clear()
        return selected if index else choices[selected]
