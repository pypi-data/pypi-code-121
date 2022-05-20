# Code from jfktrey on GitHub: https://gist.github.com/jfktrey/8928865
import platform


if platform.system() == "Windows":
    import msvcrt

    def getch():
        return msvcrt.getch().decode("utf-8")
else:
    import tty
    import termios
    import sys

    def getch():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)

        try:
            tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

        return char
