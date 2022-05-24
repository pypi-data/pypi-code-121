from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


# fmt: off
class TokenType(Enum):
    EOF             = auto()
    IDENTIFIER      = auto()
    NUMBER          = auto()
    STRING          = auto()
    COMMENT         = auto()
    IF              = auto()
    ELSE            = auto()
    WHILE           = auto()
    FOR             = auto()
    RETURN          = auto()
    BREAK           = auto()
    CONTINUE        = auto()
    TRUE            = auto()
    FALSE           = auto()
    NULL            = auto()
    IMPORT          = auto()
    AS              = auto()
    FROM            = auto()
    ASYNC           = auto()
    AWAIT           = auto()
    CLASS           = auto()
    FUNCTION        = auto()
    PUBLIC          = auto()
    EQUALS          = auto()
    GREATER         = auto()
    LESS            = auto()
    PLUS            = auto()
    MINUS           = auto()
    STAR            = auto()
    SLASH           = auto()
    BANG            = auto()
    XOR             = auto()
    COMMA           = auto()
    DOT             = auto()
    LPAREN          = auto()
    RPAREN          = auto()
    LBRACE          = auto()
    RBRACE          = auto()
    LBRACKET        = auto()
    RBRACKET        = auto()
    COLON           = auto()
    EQUALS_EQUALS   = auto()
    NOT_EQUALS      = auto()
    GREATER_EQUALS  = auto()
    LESS_EQUALS     = auto()
    AND             = auto()
    OR              = auto()
    PLUS_PLUS       = auto()
    MINUS_MINUS     = auto()
    SLASH_SLASH     = auto()
    STAR_STAR       = auto()
    ARROW           = auto()
    GREATER_GREATER = auto()
    LESS_LESS       = auto()
# fmt: on


@dataclass(slots=True, frozen=True)
class TokenMetadata:
    file: str
    line: int
    index: int


@dataclass(slots=True, frozen=True)
class Token:
    type: TokenType
    value: Optional[str]
    meta: TokenMetadata
