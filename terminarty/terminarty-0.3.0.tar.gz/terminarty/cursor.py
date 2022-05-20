from typing import Optional

CSI = '\033['


class Cursor:
    """Class, that allows for cursor controls."""
    @staticmethod
    def setpos(x: Optional[int] = 1, y: Optional[int] = 1) -> None:
        """Sets cursor position to given x and y (column and row) coordinates. Count starts from 1."""
        print(f'{CSI}{y};{x}H', end='')

    @staticmethod
    def savepos() -> None:
        """Saves current cursor position. Can be restored with ``Cursor.restorepos()``"""
        print(f'\0337', end='')

    @staticmethod
    def restorepos() -> None:
        """Restores current cursor position. Can be saved with ``Cursor.savepos()``"""
        print(f'\0338', end='')

    @staticmethod
    def up(n: Optional[int] = 1) -> None:
        """Moves cursor n lines up."""
        print(f'{CSI}{n}A', end='')

    @staticmethod
    def down(n: Optional[int] = 1) -> None:
        """Moves cursor n lines down."""
        print(f'{CSI}{n}B', end='')

    @staticmethod
    def right(n: Optional[int] = 1) -> None:
        """Moves cursor n characters right."""
        print(f'{CSI}{n}C', end='')

    @staticmethod
    def left(n: Optional[int] = 1) -> None:
        """Moves cursor n characters left."""
        print(f'{CSI}{n}D', end='')

    @staticmethod
    def hide() -> None:
        """Hides cursor."""
        print(f'{CSI}?25l', end='')

    @staticmethod
    def show() -> None:
        """Shows cursor."""
        print(f'{CSI}?25h', end='')

    @staticmethod
    def erase_line() -> None:
        """Erases line, when cursor located."""
        print(f'{CSI}2K')
