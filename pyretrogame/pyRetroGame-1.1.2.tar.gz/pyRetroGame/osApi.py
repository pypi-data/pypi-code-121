import os
import msvcrt
from .vector import Vector2

clearCommand = 'cls' if os.name == 'nt' else 'clear'

def waitKey(stdscr = None) -> int:
    x = msvcrt.kbhit()
    if x: 
        ret = ord(msvcrt.getch()) 
    else: 
        ret = 0 
    return ret

def terminalSize():
    size = os.get_terminal_size()
    return Vector2(size.columns, size.lines)
