"""Symbol table for the interpreter."""
from typing import Dict


class SymbolTable(Dict[str, str]):
    """A dictionary like structure to store local variables."""
