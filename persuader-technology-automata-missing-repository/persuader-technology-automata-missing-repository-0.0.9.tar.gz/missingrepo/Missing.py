from dataclasses import dataclass

from core.missing.Context import Context


@dataclass
class Missing:
    missing: str
    context: Context
    market: str
    description: str

    def __eq__(self, other):
        return f'{self.missing}{self.context.value}{self.market}' == f'{other.missing}{other.context.value}{other.market}'
