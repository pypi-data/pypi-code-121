from .context.tokens import *
from .context import base
from .util import listify
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
    # KEYWORD: "keyword",
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

    # Must come last so it doesn't override custom words
    # Maybe separate type?
    WORD: "words",
}


# May add a "name" to this
Symbol = namedtuple("Symbol", ("pattern", "property"))


class Context(namedtuple("Context", ttypes.values())):
    ttypes = ttypes

    @staticmethod
    def symbols(symbols):
        return list(map(Symbol._make, symbols.items()))

    @classmethod
    def from_base(cls):
        glyph = cls._make(cls.symbols(getattr(base, name)) for name in cls._fields)
        glyph.normalize()

        return glyph

    @classmethod
    def from_namespace(cls, context):
        glyph = cls._make(cls.symbols(getattr(context, name, {})) for name in cls._fields)
        glyph.normalize()

        return glyph

    @staticmethod
    def _normalize_symbol(attrib):
        if isinstance(attrib, tuple):
            return attrib
        elif isinstance(attrib, str):
            return (attrib, {})
        else:
            raise TypeError(f"Unknown type {type(attrib)} for {attrib}")

    def _normalize(self, symbols):
        for i, symbol in enumerate(symbols):
            symbols[i] = symbol._replace(
                property=self._normalize_symbol(symbol.property))

    def normalize(self):
        for symbols in [
            self.operators,
            self.binary_operators,
            self.relations,
            self.functions,
            self.identifiers,
            self.brackets,
        ]:
            self._normalize(symbols)

    def items(self):
        # ttype_name is aligned with Glyph
        yield from zip(ttypes, self)


class Glyph:
    areas = []
    index = {}
    flags = flags

    def __init__(self, areas, index):
        # Note: instance attributes are different from class attributes
        self.areas = areas
        self.index = index

    @classmethod
    def _get(cls, area):
        # Lazy getter
        context = cls.areas[cls.index[area]]
        if not isinstance(context, Context):
            if isinstance(context, str):
                context = import_module(context)
            elif isinstance(context, ModuleType):
                pass
            elif isinstance(context, dict):
                context = SimpleNamespace(**context)
            else:
                raise TypeError(f"Invalid type '{type(context)}' for area.")

            context = Context.from_namespace(context)
            cls.areas[cls.index[area]] = context
        return context

    @classmethod
    @cache
    def from_area(cls, area=None, base=True):
        areas = listify(area)
        if base is True:
            areas = areas + ("base",)

        index = {area: cls.index[area] for area in areas}
        areas = [cls._get(area) for area in areas]

        return cls(areas, index)


    @classmethod
    def register_area(cls, area, context):
        # TODO: Handle overwrites?
        assert area not in cls.index
        cls.areas.append(context)
        cls.index[area] = cls.areas.index(context)

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

    def __iter__(self):
        for i, area in enumerate(self.areas):
            for j, (ttype, symbols) in enumerate(area.items()):
                for k, symbol in enumerate(symbols):
                    yield (i, j, k), ttype, symbol

    def patterns(self):
        for ijk, ttype, symbol in self:
            yield ijk, ttype, symbol.pattern

    def __getitem__(self, key):
        k0, k1, k2 = key
        return self.areas[k0][k1][k2]

    def property(self, key, default=None):
        try:
            return self[key].property
        except KeyError:
            return default


# This should probably be defined at instance-level
# But that requires some refactoring
Glyph.register_areas({
    "base": "mumath.context.base",
    "physics": "mumath.context.physics",
    "chemistry": "mumath.context.chemistry",
    "statistics": "mumath.context.statistics",
})
Glyph.register_extensions()
