"Module for reading legacy format LXTSV (similar to CONLL)"

from lxcommon.lxsentence import LxSentence


def read_lxtsv(lines):
    """Reads and yields sentences as Python lists of dicts (each token is a dict)"""
    enumerated_lines = enumerate(lines, start=1)

    expected_column_names = [
        "form",
        "raw",
        "lemma",
        "pos",
        "infl",
        "ne",
        "deprel",
        "parent",
        "udeprel",
        "uparent",
        "space",
    ]

    # first line should contain column names; sanity check here:
    for linenum, line in enumerated_lines:
        column_names = line.rstrip("\n").split("\t")
        if column_names != expected_column_names:
            raise Exception(
                f"Unexpected column names in first line; got {column_names}; "
                f"expected {expected_column_names}."
            )
        break
    else:  # file is empty
        return

    sentence = []
    for linenum, line in enumerated_lines:
        line = line.rstrip("\n")
        if not line:
            if sentence:
                yield sentence
                sentence = []
        else:
            columns = line.split("\t")
            if len(columns) != len(column_names):
                raise Exception(
                    f"Unexpected number of columns in line {linenum}; "
                    f"expected {len(column_names)}, got {len(columns)}."
                )
            sentence.append(dict(zip(column_names, columns)))
    if sentence:
        yield sentence


def read_lxsentences_from_lxtsv(lines):
    for sentence in read_lxtsv(lines):
        yield LxSentence.from_primitive_types(sentence)
