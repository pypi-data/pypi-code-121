from enum import Enum

from typing import List, Tuple as TTuple


class IOType(str, Enum):
    val = 'val'
    file = 'file'
    path = 'path'
    env = 'env'
    stdout = 'stdout'
    tuple = 'tuple'
    stdin = 'stdin'
    each = 'each'


class InOut:
    type: IOType
    value: str

    def __init__(self, type: IOType, value: str):
        self.type = type
        self.value = value

    def __repr__(self):
        quote = "\"" if "$" in self.value else ""
        return f"{self.type.value}({quote}{self.value}{quote})"


class Val(InOut):
    def __init__(self, value):
        InOut.__init__(self, IOType.val, value)


class Path(InOut):
    def __init__(self, value):
        InOut.__init__(self, IOType.path, value)


class Tuple(InOut):
    values: List[InOut]

    def __init__(self, *values: List[InOut]):
        InOut.__init__(self, IOType.tuple, "")
        self.type = IOType.tuple
        self.values = values

    def __repr__(self):
        str_values = ", ".join([v.__repr__() for v in self.values])
        return f"tuple {str_values}"


class Bash:
    pass


class Python:
    pass


class Channel:
    body: str

    def __init__(self, body: str):
        self.body = body

    def __repr__(self):
        return self.body

    def _generator(self):
        pass

    def combine(self, ch):
        return Channel(f"{self.body}.combine({repr(ch)})")


class Variable:
    name: str
    dollar: bool
    quotes: bool

    def __init__(self, name: str, dollar: bool = False, quotes: bool = False):
        self.name = name
        self.dollar = dollar
        self.quotes = quotes

    def __repr__(self):
        result = f"${{{self.name}}}" if self.dollar else self.name
        result = f"\"{result}\"" if self.quotes else result
        return result

    def __getitem__(self, item):
        return Variable(f"{self.name}[{item}]", dollar=self.dollar)
