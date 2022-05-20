# Code from jfktrey on GitHub: https://gist.github.com/jfktrey/8928865
import platform


if platform.system() == "Windows":
    import msvcrt

    def getwch() -> str:
        '''
        Cross platform version of `getwch()`.

        Wide variant of `getch()`, returning a Unicode value.
        '''

        return msvcrt.getwch()
else:
    import tty
    import termios
    import sys

    def getwch() -> str:
        '''
        Cross platform version of `getwch()`.

        Wide variant of `getch()`, returning a Unicode value.
        '''

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)

        try:
            tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

        return char
