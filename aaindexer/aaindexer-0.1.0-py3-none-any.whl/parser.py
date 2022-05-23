"""
Pyparsing grammar and elements
"""
from pyparsing import *
from pyparsing import common
from string import ascii_uppercase
from itertools import chain
from aaindexer.models import AaindexRecord


def visit_general_field(s, loc, toks):
    key, *value = toks
    value = " ".join(value)

    # If the field was empty, just set it to None
    if len(value.strip()) == 0:
        return key, None

    return key, value


def visit_corr_field(s, loc, toks):
    if len(toks) == 0:
        return None
    else:
        return "correlation", dict(list(toks))


def visit_index_field(s, loc, toks):
    names, values = toks
    ordered_names = list(chain.from_iterable(zip(*names)))
    pairs = dict(list(zip(ordered_names, values)))
    return "index", pairs


def visit_matrix_field(s, loc, toks):
    row_names, col_names, *rows = toks

    return "matrix", {row_name: dict(zip(col_names, row)) for row_name, row in zip(row_names, rows)}


def visit_record(s, loc, toks):
    return AaindexRecord(**dict(list(toks)))


FIELD_NAMES = {
    "H": "accession",
    "D": "description",
    "R": "pmid",
    "A": "authors",
    "T": "title",
    "J": "journal",
    "C": "correlation",
    "I": "index",
    "M": "matrix",
    "*": "comment"
}


def visit_general_field_name(s, loc, toks):
    return FIELD_NAMES[toks[0]]


def grouper(s, loc, toks):
    return [list(toks)]


def visit_na(s, loc, toks):
    return [None]


#: Always returns a float
numeric = common.number | (Literal("NA") | Literal("-")).add_parse_action(visit_na)

general_field_name = (
    Char(set(FIELD_NAMES.keys()) - {"I", "C", "M"})
        .set_name("general_field_name")
        .add_parse_action(visit_general_field_name)
)
record_footer = (Literal("//") + LineEnd()).set_name("record_footer").suppress()
header_sep = Literal(" ").set_name("header_sep").suppress()
general_field_contents = SkipTo(LineEnd()) + LineEnd().suppress()
general_field_line = (Literal("  ").suppress() + general_field_contents).set_name(
    "general_field_line"
)
general_field = (
    (
            general_field_name
            + (
                    (header_sep + general_field_contents + Opt(general_field_line[1, ...]))
                    ^ LineEnd()
            )
    )
        .set_name("general_field")
        .set_parse_action(visit_general_field)
)
aa_name = (
    (Char(ascii_uppercase) + Literal("/").suppress() + Char(ascii_uppercase))
        .set_name("aa_name")
        .add_parse_action(grouper)
)

index_field = (
    (
            Literal("I").suppress()
            + White().suppress()
            + delimited_list(aa_name, delim=White()).add_parse_action(grouper)
            + White().suppress()
            + delimited_list(numeric, delim=White(), allow_trailing_delim=False
                             ).add_parse_action(grouper)
            + LineEnd().suppress()
    )
        .set_name("index_field")
        .add_parse_action(visit_index_field)
)

corr_entry = (
    (Word(alphanums) + White().suppress() + common.real)
        .set_name("corr_entry")
        .set_parse_action(grouper)
)
corr_field = (
    (
            Literal("C").suppress()
            + Optional(
        (
                header_sep
                + delimited_list(corr_entry, delim=White())
        )
        ^ White(" ").suppress()
    )
            + LineEnd().suppress()
    )
        .set_name("corr_field")
        .add_parse_action(visit_corr_field)
)
matrix_names = Word(ascii_uppercase + "-")
matrix_field = (
    (
            Literal("M").suppress()
            + header_sep
            + Literal("rows = ").suppress()
            + matrix_names.copy().set_name("matrix_row_labels")
            + Literal(", ").suppress()
            + Literal("cols = ").suppress()
            + matrix_names.copy().set_name("matrix_column_labels")
            + LineEnd().suppress()
            + delimited_list(
        White().suppress() + delimited_list(numeric, White(" "),
                                            allow_trailing_delim=True).add_parse_action(grouper),
        delim="\n",
        allow_trailing_delim=True
    )
    )
        .set_name("matrix_field")
        .add_parse_action(visit_matrix_field)
)
aaindex_field = (index_field ^ corr_field ^ matrix_field ^ general_field).set_name(
    "aaindex_record"
)

aaindex_record = (
    (aaindex_field[1, ...] + record_footer)
        .set_name("aaindex_record")
        .add_parse_action(visit_record)
).leave_whitespace(recursive=True)

aaindex_file = (
    aaindex_record[1, ...].set_name("aaindex_file").leave_whitespace().add_parse_action(
        lambda s, loc, toks: list(toks))
)
