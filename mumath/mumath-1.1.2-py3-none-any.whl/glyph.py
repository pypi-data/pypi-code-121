from .context.tokens import *
from .context import base
from .util import listify
import re
from importlib import import_module
from collections import namedtuple
from types import ModuleType, SimpleNamespace

try:
    from functools import cache
except importError:
    from functools import lru_cache as cache


# For diffs
# The functions look weird, but they set the first and second bit
# to either 0 or 1. E.g. `(+1).__or__(0b00) == 0b01`.
flags = {
    OPEN_NEXT: (+1).__or__,
    SHUT_NEXT: (~1).__and__,
    OPEN_PREV: (+2).__or__,
    SHUT_PREV: (~2).__and__,
}


ttypes = {
    # basic syntactical components
    KEYWORD: "keyword",
    TEXT_SEP: "text_separator",
    SUBB: "subb",
    SUB: "sub",
    SUPP: "supp",
    SUP: "sup",
    OPEN_NEXT: "open_next",
    SHUT_NEXT: "shut_next",
    OPEN_PREV: "open_prev",
    SHUT_PREV: "shut_prev",
    SOFT_SPACE: "soft_space",
    STRING: "string",
    COMMENT: "comment",

    # basic functional components
    MATRIX: "matrix",
    BEGIN: "begin",
    END: "end",
    ENVIRONMENT: "environments",
    OVER: "over",
    CHOOSE: "choose",
    SERIES: "series",  # macro
    SQRT: "sqrt",
    CLASS_: "class_",
    TEXT: "text",
    NO_NUMBER: "no_number",
    PRESCRIPT: "prescript",
    UNDERSET: "underset",
    OVERSET: "overset",
    FRAC: "frac",
    BINOM: "binom",
    ROOT: "root",
    DISPLAYSTYLE: "displaystyle",
    PAD: "pad",

    # general components
    RELATION: "relations",
    IDENTIFIER: "identifiers",
    OPERATOR: "operators",
    BINOP: "binary_operators",
    FUNCTION: "functions",
    NORM: "brackets",

    NUMBER: "numbers",
    HAT: "hats",
    SHOE: "shoes",
    OPEN: "open_brackets",
    CLOSE: "close_brackets",
    COL_SEP: "col_separators",
    ROW_SEP: "row_separators",
    VARIANT: "fonts",
    ENCLOSE: "enclosures",
    SPACE: "spaces",
}


class Glyph(namedtuple("Glyph", ttypes.values())):
    areas = {}
    flags = flags

    @classmethod
    def from_base(cls):
        glyph = cls._make(getattr(base, name).copy() for name in cls._fields)

        glyph.identifiers.update(base.custom_identifiers)
        glyph.identifiers.update(base.sets)
        glyph.identifiers.update(base.greeks)
        glyph.identifiers.update(base.chemistry)
        glyph.identifiers.update(base.physics)
        glyph.functions.update(base.custom_functions)

        glyph.normalize()

        return glyph

    @classmethod
    def empty(cls):
        return cls._make({} for _ in cls._fields)

    @classmethod
    def from_namespace(cls, area):
        glyph = cls._make(getattr(area, name, {}).copy() for name in cls._fields)
        glyph.normalize()

        return glyph

    @classmethod
    def _get(cls, area):
        # Lazy getter
        context = cls.areas[area]
        if not isinstance(context, Glyph):
            if isinstance(context, str):
                context = import_module(context)
            elif isinstance(context, ModuleType):
                pass
            elif isinstance(context, dict):
                context = SimpleNamespace(**context)
            else:
                raise TypeError(f"Invalid type '{type(context)}' for area.")

            context = cls.from_namespace(context)
            cls.areas[area] = context
        return context

    @classmethod
    @cache
    def from_area(cls, area=None, base=True):
        if base is True:
            glyph = cls.from_base()
        elif base is False:
            glyph = cls.empty()
        elif isinstance(base, Glyph):
            glyph = base
        else:
            raise TypeError(f"Invalid type '{type(base)}' for base.")

        areas = listify(area)
        for area in areas:
            glyph += cls._get(area)

        return glyph

    def __iadd__(self, other):
        for old, new in zip(self, other):
            old.update(new)
        return self

    @classmethod
    def register_area(cls, area, context):
        cls.areas[area] = context

    @classmethod
    def register_areas(cls, area=None, **areas):
        if area is None:
            for area, context in areas.items():
                cls.register_area(area, context)
        if isinstance(area, dict):
            for area, context in area.items():
                cls.register_area(area, context)
        else:
            raise TypeError(f"Invalid type {type(area)} for area.")


    @classmethod
    def register_extensions(cls):
        # from importlib import metadata
        # metadata.entry_points(group="mumath.extensions")
        pass

    def _ttype_name(self):
        # ttype_name is aligned with Glyph
        return {ttype: key for ttype, key in zip(ttypes, self)}

    def normalize(self):
        self.operators.update(normalize(self.operators))
        self.binary_operators.update(normalize(self.binary_operators))
        self.relations.update(normalize(self.relations))
        self.functions.update(normalize(self.functions))
        self.identifiers.update(normalize(self.identifiers))
        self.brackets.update(normalize(self.brackets))

    @property
    def tokens(self):
        return dict(_tokens(self._ttype_name()))

    @property
    def keywords(self):
        return dict(_keywords(self._ttype_name()))


# This should probably be defined at instance-level
# But that requires some refactoring
Glyph.register_areas({
    "chemistry": "mumath.context.chemistry",
    "statistics": "mumath.context.statistics",
})
Glyph.register_extensions()


# Match words without _ and numbers
_keyword = r"\\[^\W\d_]+$"
_word = r"[^\W\d_]+"


def group_symbols(groups):
    for ttype, symbols in groups.items():
        for symbol in symbols:
            yield (ttype, symbol)


def _tokens(groups):
    for ttype, symbol in group_symbols(groups):
        if not re.match(_keyword, symbol):
            yield (symbol, ttype)

    # Must come last so it doesn't override custom words
    # Maybe separate type?
    yield (_word, IDENTIFIER)


def _keywords(groups):
    for ttype, symbol in group_symbols(groups):
        if re.match(_keyword, symbol):
            yield (symbol, ttype)


def _normalize(attrib):
    if isinstance(attrib, tuple):
        return attrib
    elif isinstance(attrib, str):
        return (attrib, {})
    else:
        raise TypeError(f"Unknown type {type(attrib)} for {attrib}")


def normalize(dict_):
    return {key: _normalize(value) for key, value in dict_.items()}


def merge(dicts):
    return {key: value for d in dicts for key, value in d.items()}
