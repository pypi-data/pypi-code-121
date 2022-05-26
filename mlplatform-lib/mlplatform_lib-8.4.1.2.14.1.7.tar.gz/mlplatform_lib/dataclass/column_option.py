from dataclasses import dataclass


@dataclass
class ColumnOption:
    name: str
    alias: str
    type: str
