# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring

from typing import List
from chiakilisp.models.token import Token
from chiakilisp.models.operand import Operand
from chiakilisp.models.expression import Expression


Child = Operand or Expression  # define a type for the single child
Children = List[Child]  # define a type describing list of children


class Parser:

    """Parser is the class that takes a list of tokens and produces a wood of Expressions or Operands"""

    _tokens: List[Token]
    _wood: List[Operand or Expression]

    def __init__(self, tokens: List[Token]) -> None:

        """Initialize Parser instance"""

        self._tokens = tokens
        self._wood = []

    def parse(self) -> None:

        """Process a list of tokens in order to populate complete wood"""

        self._wood = read(self._tokens)  # utilizes dedicated read() func

    def wood(self) -> List[Operand or Expression]:

        """Its a getter for private _wood field"""

        return self._wood


def find_nearest_closing_bracket(filtered: list, visited: list) -> tuple:

    """This function takes a token collection listing and finds the nearest closing bracket position"""

    _all = tuple(filter(lambda p: p not in visited and p[1].type() == Token.ClosingBracket, filtered))
    if not _all:
        raise AssertionError('Parser::find_nearest_closing_bracket() there is no nearest ClosingBracket')
    return _all[0]


def find_nearest_opening_bracket(filtered: list, visited: list) -> tuple:

    """This function takes a token collection listing and finds the nearest opening bracket position"""

    _all = tuple(filter(lambda p: p not in visited and p[1].type() == Token.OpeningBracket, filtered))
    if not _all:
        raise AssertionError('Parser::find_nearest_closing_bracket() there is no nearest OpeningBracket')
    return _all[0]


def boundary(lst: List[Token]) -> int:

    """This function takes a token collection listing and finds actual boundary to starting expression"""

    assert len(lst) >= 2 and lst[0].type() == Token.OpeningBracket  # non-empty tokens list, first should be a '('

    filtered: list  # for some reason, pylint confuses about filtered type assuming it is the same type as the lst

    filtered = list(filter(lambda p: p[1].type() in [Token.OpeningBracket, Token.ClosingBracket], enumerate(lst)))

    starting_opening_bracket = filtered[0]
    starting_opening_bracket_position = starting_opening_bracket[0]

    visited = []  # define list of bracket' tokens we've already visited

    while True:
        if not filtered:
            return -1  # return '-1' if there are no more bracket tokens

        nearest_closing_bracket = find_nearest_closing_bracket(filtered, visited)
        nearest_closing_bracket_position = nearest_closing_bracket[0]

        reversed_filtered = list(reversed(filtered[:filtered.index(nearest_closing_bracket) + 1]))

        nearest_opening_bracket_to_that_closing = find_nearest_opening_bracket(reversed_filtered, visited)
        nearest_opening_bracket_to_that_closing_position = nearest_opening_bracket_to_that_closing[0]

        if nearest_opening_bracket_to_that_closing_position == starting_opening_bracket_position:
            return nearest_closing_bracket_position  # if matches exact same position -> valid expression boundary

        visited.append(nearest_closing_bracket)
        visited.append(nearest_opening_bracket_to_that_closing)  # and append these two tokens to the visited list


def read(tokens: List[Token]) -> Children:

    """This function produces wood of Expressions/Operands"""

    if not tokens:
        return []  # allow empty expressions, useful for defn

    children: Children = []

    idx: int = 0
    while idx < len(tokens):
        current_token = tokens[idx]
        if current_token.type() == Token.OpeningBracket:  # if read() function has encountered an expression start
            boundary_of_encountered_expression: int = boundary(tokens[idx:])  # find an idx of expression boundary
            left_boundary, right_boundary = idx + 1, boundary_of_encountered_expression + idx  # define boundaries
            children.append(Expression(read(tokens[left_boundary:right_boundary])))  # an expression children list
            idx = right_boundary + 1  # and then let the read() function to advance to the next one token instance
        else:
            children.append(Operand(current_token))  # in case current token is a regular one, treat it as Operand
            idx += 1  # and let the read() function to advance to the next one token by incrementing an index to 1

    return children  # in the end return a list of an Expression children (Operands or child Expression instances)
