import black
import parso

from globality_black.blank_lines import cover_blank_lines, uncover_blank_lines
from globality_black.common import SyntaxTreeVisitor
from globality_black.comprehensions import reformat_comprehension
from globality_black.constants import (
    BLANK_LINES_TYPES,
    COMPREHENSIONS_TYPES,
    DOTTED_CHAIN_TYPES,
    TUPLE_TYPES,
)
from globality_black.dotted_chains import cover_dotted_chain_if_needed, uncover_dotted_chain
from globality_black.tuples import cover_tuple_if_needed, uncover_tuple


class BlackError(Exception):
    pass


def reformat_text(file_contents, black_mode):

    module = parso.parse(file_contents)

    # PRE-PROCESSING

    # cover blank lines if needed
    finder = SyntaxTreeVisitor(module, BLANK_LINES_TYPES)
    for element in finder(module):
        cover_blank_lines(module, element)

    # cover dotted chains
    finder = SyntaxTreeVisitor(module, DOTTED_CHAIN_TYPES)
    for element in finder(module):
        cover_dotted_chain_if_needed(element)

    # cover size one tuples
    # TODO: remove this once/if https://github.com/psf/black/issues/1139#issuecomment-951014094
    #  solved
    finder = SyntaxTreeVisitor(module, TUPLE_TYPES)
    for element in finder(module):
        cover_tuple_if_needed(element)

    # BLACK

    try:
        code_after_black = black.format_str(module.get_code(), mode=black_mode)
    except Exception as e:
        raise BlackError(e)

    module = parso.parse(code_after_black)

    # POST-PROCESSING

    # comprehensions
    finder = SyntaxTreeVisitor(module, COMPREHENSIONS_TYPES)
    for element in finder(module):
        if element.type == "sync_comp_for":
            reformat_comprehension(element)

    # uncover blank lines protected during pre-processing
    finder = SyntaxTreeVisitor(module, BLANK_LINES_TYPES)
    for element in finder(module):
        uncover_blank_lines(module, element)

    # uncover lines from dotted chains protected during pre-processing
    finder = SyntaxTreeVisitor(module, DOTTED_CHAIN_TYPES)
    for element in finder(module):
        uncover_dotted_chain(module, element)

    # cover size one tuples
    # TODO: remove this once/if https://github.com/psf/black/issues/1139#issuecomment-951014094
    #  solved
    finder = SyntaxTreeVisitor(module, TUPLE_TYPES)
    for element in finder(module):
        uncover_tuple(module, element)

    return module.get_code()
