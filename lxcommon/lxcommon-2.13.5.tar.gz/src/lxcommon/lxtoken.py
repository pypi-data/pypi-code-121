"""
Luís Gomes <luis.gomes@di.fc.ul.pt>, <luismsgomes@gmail.com>

Copyright NLX-Group, Universidade de Lisboa, 2015-2022
"""

import logging

from .cintilformat import (
    parse_cintil_token,
    format_cintil_token,
)

from .utils import normalize_unicode, recase_as
from .tagsets import (
    LX_POS_TAGS,
    U_POS_TAGS,
    LX_DEPREL_TAGS,
    U_DEPREL_TAGS,
    U_DEPREL_TAGS_V1_TO_V2,
    LX_FEATS,
    U_FEATS,
    NE_TAGS,
)


LOG = logging.getLogger(__name__)


class LxToken:
    _attrs = [
        "form",
        "raw",
        "lemma",
        "pos",
        "_upos",
        "feats",
        "ufeats",
        "ne",
        "ne_rb",
        "deprel",
        "parent",
        "_udeprel",
        "uparent",
        "space",
    ]

    def __init__(
        self,
        form,
        space="LR",
        raw=None,
        pos=None,
        upos=None,
        lemma=None,
        ulemma=None,
        feats=None,
        ufeats=None,
        infl=None,
        uinfl=None,
        ne=None,
        ne_rb=None,
        deprel=None,
        parent=None,
        udeprel=None,
        uparent=None,
        **kwargs,
    ):
        self.form = normalize_unicode(form)
        self.space = ""
        self.add_space(space)
        self.raw = normalize_unicode(raw) if isinstance(raw, str) else raw
        self.pos = pos
        self.upos = upos
        self.lemma = lemma
        self.ulemma = ulemma
        if feats is not None:
            if infl is not None and infl != feats:
                raise ValueError(
                    "Attributes feats and infl cannot be given simultaneously "
                    "and with different values."
                )
        if ufeats is not None:
            if uinfl is not None and uinfl != ufeats:
                raise ValueError(
                    "Attributes ufeats and uinfl cannot be given simultaneously "
                    "and with different values."
                )
        self.feats = feats or infl
        self.ufeats = ufeats or uinfl
        self.ne = ne
        self.ne_rb = ne_rb
        self.deprel = deprel
        self.parent = parent
        self.udeprel = udeprel
        self.uparent = uparent
        for name, value in kwargs.items():
            setattr(self, name, value)

    @property
    def udeprel(self):
        return self._udeprel

    @udeprel.setter
    def udeprel(self, udeprel):
        self._udeprel = udeprel.lower() if udeprel else None

    @property
    def upos(self):
        return self._upos

    @upos.setter
    def upos(self, upos):
        self._upos = upos.upper() if upos else None

    @property
    def infl(self):
        return self.feats

    @infl.setter
    def infl(self, feats):
        self.feats = feats

    @property
    def uinfl(self):
        return self.ufeats

    @uinfl.setter
    def uinfl(self, ufeats):
        self.ufeats = ufeats

    def __eq__(self, other):
        return isinstance(other, LxToken) and self.__dict__ == other.__dict__

    def add_space(self, where):
        for c in where.upper():
            if c not in ["L", "R"]:
                raise ValueError(f"Invalid character {c!r} in where")
            if c not in self.space:
                if c == "L":
                    self.space = c + self.space
                else:
                    self.space = self.space + c

    def remove_space(self, where):
        for c in where.upper():
            if c not in ["L", "R"]:
                raise ValueError(f"Invalid character {c!r} in where")
            if c in self.space:
                self.space = self.space.replace(c, "")

    @staticmethod
    def from_primitive_types(token):
        if not isinstance(token, dict):
            raise TypeError("token must be a dict")
        form = token["form"]
        attrs = {a: v if v != "_" else None for a, v in token.items() if a != "form"}
        return LxToken(form, **attrs)

    def to_primitive_types(self, empty_attrs=False, extra_attrs=True, infl=False):
        attr_name_mapping = {"_upos": "upos", "_udeprel": "udeprel"}
        if infl:
            attr_name_mapping["feats"] = "infl"
        if extra_attrs:
            return {
                attr_name_mapping.get(attr, attr): value
                for attr, value in self.__dict__.items()
                if empty_attrs or value is not None
            }
        return {
            attr_name_mapping.get(attr, attr): getattr(self, attr, None)
            for attr in LxToken._attrs
            if empty_attrs or getattr(self, attr, None) is not None
        }

    def to_cintil(self, format_spec):
        return format_cintil_token(self.to_primitive_types(), format_spec)

    @staticmethod
    def from_cintil(token, format_spec):
        return LxToken.from_primitive_types(parse_cintil_token(token, format_spec))

    def copy(self):
        return LxToken(
            self.form,
            **{attr: value for attr, value in self.__dict__.items() if attr != "form"},
        )

    def strip_pos(self):
        self.pos = None

    def strip_upos(self):
        self.upos = None

    def strip_morph(self):
        self.lemma = None
        self.feats = None

    def strip_umorph(self):
        self.ulemma = None
        self.ufeats = None

    def strip_ne(self):
        self.ne = None

    def strip_ne_rb(self):
        self.ne_rb = None

    def strip_dep(self):
        self.deprel = None
        self.parent = None

    def strip_udep(self):
        self.udeprel = None
        self.uparent = None

    def istag(self):
        # this may give false positives but it's better to be on the safe side
        return self.form.startswith("<") and self.form.endswith(">")

    def upgrade_udeprel(self):
        if self.udeprel in U_DEPREL_TAGS_V1_TO_V2:
            self.udeprel = U_DEPREL_TAGS_V1_TO_V2[self.udeprel]

    def check_tagsets(self):
        errors = {}
        if self.pos and self.pos not in LX_POS_TAGS:
            errors["pos"] = self.pos
        if self.upos and self.upos not in U_POS_TAGS:
            errors["upos"] = self.upos

        if self.deprel and self.deprel not in LX_DEPREL_TAGS:
            errors["deprel"] = self.deprel
        if self.udeprel and self.udeprel not in U_DEPREL_TAGS:
            errors["udeprel"] = self.udeprel

        if self.feats and self.feats not in LX_FEATS:
            errors["feats"] = self.feats
        if self.ufeats and self.ufeats not in U_FEATS:
            errors["ufeats"] = self.ufeats

        if self.ne and self.ne not in NE_TAGS:
            errors["ne"] = self.ne
        return errors

    def __repr__(self):
        attr_name_mapping = {"_upos": "upos", "_udeprel": "udeprel"}
        attrs = ", ".join(
            [
                f"{attr_name_mapping.get(attr, attr)}={value!r}"
                for attr, value in sorted(self.__dict__.items())
                if attr != "form" and value is not None
            ]
        )
        return f"LxToken({self.form!r}, {attrs})"

    @property
    def recased_form(self):
        return recase_as(self.form, self.raw) if self.raw else self.form


__all__ = ["LxToken"]
