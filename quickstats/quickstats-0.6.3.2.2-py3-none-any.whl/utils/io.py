import sys
import difflib
from enum import Enum
from typing import Union
from functools import total_ordering

text_color_map = {
    None: '',
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'bright black': '\033[30;1m',
    'bright red': '\033[31;1m',
    'bright green': '\033[32;1m',
    'bright yellow': '\033[33;1m',
    'bright blue': '\033[34;1m',
    'bright magenta': '\033[35;1m',
    'bright cyan': '\033[36;1m',
    'bright white': '\033[37;1m',    
    'darkred': '\033[91m',
    'reset': '\033[0m'
}

def get_colored_text(text:str, color:str):
    return f"{text_color_map[color]}{text}{text_color_map['reset']}"

def format_comparison_text(text_left:str, text_right:str,
                           equal_color=None, delete_color:str="red", insert_color:str="green"):
    codes = difflib.SequenceMatcher(a=text_left, b=text_right).get_opcodes()
    s_left  = ""
    s_right = ""
    for code in codes:
        if code[0] == "equal":
            s = get_colored_text(text_left[code[1]:code[2]], equal_color)
            s_left  += s
            s_right += s
        elif code[0] == "delete":
            s_left  += get_colored_text(text_left[code[1]:code[2]], delete_color)
        elif code[0] == "insert":
            s_right += get_colored_text(text_right[code[3]:code[4]], insert_color)
        elif code[0] == "replace":
            s_left  += get_colored_text(text_left[code[1]:code[2]], delete_color)
            s_right += get_colored_text(text_right[code[3]:code[4]], insert_color)
    return s_left, s_right

@total_ordering
class Verbosity(Enum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        elif isinstance(other, int):
            return self.value < other
        elif isinstance(other, str):
            return self.value < getattr(self, other.upper()).value
        return NotImplemented

class VerbosePrint:
    @property
    def verbosity(self):
        return self._verbosity
    
    @verbosity.setter
    def verbosity(self, val):
        if isinstance(val, str):
            try:
                v = getattr(Verbosity, val.upper())
            except:
                raise ValueError("invalid verbosity level: {}".format(val))
            self._verbosity = v
        else:
            self._verbosity = val

    def __init__(self, verbosity:Union[int, Verbosity, str]=Verbosity.INFO):
        self.verbosity = verbosity
        
    def info(self, text:str, color=None):
        self.__call__(text, Verbosity.INFO, color=color)
        
    def warning(self, text:str, color=None):
        self.__call__(text, Verbosity.WARNING, color=color)
        
    def error(self, text:str, color=None):
        self.__call__(text, Verbosity.ERROR, color=color)
        
    def critical(self, text:str, color=None):
        self.__call__(text, Verbosity.CRITICAL, color=color)

    def debug(self, text:str, color=None):
        self.__call__(text, Verbosity.DEBUG, color=color)
        
    def __call__(self, text:str, verbosity:int=Verbosity.INFO,
                 color=None):
        if color:
            text = f"{text_color_map[color]}{text}{text_color_map['reset']}"
        if verbosity >= self.verbosity:
            sys.stdout.write(f"{text}\n")