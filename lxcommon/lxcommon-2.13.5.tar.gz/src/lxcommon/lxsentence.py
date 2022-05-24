import re
from .cintilformat import (
    parse_cintil_sentence,
    format_cintil_sentence,
)
from .conllformat import format_conll_sentence
from .lxtoken import LxToken
from .penn import escape_token
from .utils import normalize_unicode

import lxcommon.conllx


class LxSentence(list):
    def __init__(
        self,
        *tokens,
        raw=None,
        default_cintil_format_spec=None,
        ctree=None,
        sent_id=None,
        par_id=None,
    ):
        if raw is not None:
            if not isinstance(raw, str):
                raise TypeError("raw must be a string")
        if not all(isinstance(token, LxToken) for token in tokens):
            raise TypeError("all tokens must be instances of LxToken")
        super().__init__(tokens)
        self.raw = normalize_unicode(raw) if isinstance(raw, str) else raw
        self.ctree = ctree
        self.default_cintil_format_spec = default_cintil_format_spec
        self.sent_id = sent_id
        self.par_id = par_id

    # TODO: maybe this property should be set when LxTokenizer is run on this sentence
    @property
    def tokenized(self):
        return len(self) > 0 or self.raw is None or self.raw.strip() == ""

    # TODO: maybe this property should be set when LxTagger is run on this sentence
    @property
    def tagged(self):
        return self.tokenized and all(token.pos is not None for token in self)

    # TODO: maybe this property should be set when LxSuite is run on this sentence
    @property
    def analysed(self):
        return (
            self.tokenized
            and self.tagged
            and (
                any(token.feats is not None for token in self)
                or any(token.lemma is not None for token in self)
            )
        )

    def upgrade_udeprels(self):
        "Upgrades Universal Dependency relations from V1 to V2"
        for token in self:
            token.upgrade_udeprel()
        return self

    def check_tagsets(self):
        sentence_errors = []
        for pos, token in enumerate(self, start=1):
            token_errors = token.check_tagsets()
            if token_errors:
                sentence_errors.append((pos, token_errors))
        return sentence_errors

    def get_ctree_pseudotags(self):
        pseudotags = []
        pattern = r"(?P<left>[^\)]+) (?P<token>[^\)]*)(?P<right>\)+)(?: |$)"
        ctree = getattr(self, "ctree", None)
        if not ctree:
            raise Exception("sentence has no ctree")
        matches = re.findall(pattern, ctree)
        if len(matches) != len(self):
            raise Exception(
                "ctree is inconsistent with sentence tokens; "
                f"ctree seems to have {len(matches)} tokens; expected {len(self)}"
            )
        for (left, form, right), token in zip(matches, self):
            if form != escape_token(token.form):
                raise Exception(
                    "ctree is inconsistent with sentence tokens; "
                    f"expected {token.form}, found {form}"
                )
            pseudotags.append(left.replace(" ", "") + "*" + right.replace(" ", ""))
        return pseudotags

    def to_plain_text(self):
        if self.raw:
            return self.raw
        buffer = []
        for token in self:
            if "L" in token.space:
                buffer.append(" ")
            if token.raw:
                buffer.append(token.raw)
        return "".join(buffer)

    def to_cintil(self, format_spec=None):
        if format_spec is None:
            if self.default_cintil_format_spec is None:
                raise ValueError(
                    "format_spec cannot be None "
                    "because self.default_cintil_format_spec is None"
                )
            format_spec = self.default_cintil_format_spec
        return format_cintil_sentence(self.to_primitive_types(), format_spec)

    def to_conll(self, universal_deps=False, universal=False, empty="-"):
        # FIXME: should save other sentence attributes, such as sent_id
        # FIXME: could also save the plain text sentence in a comment
        return format_conll_sentence(
            self.to_primitive_types(),
            universal_deps=universal_deps,
            universal=universal,
            empty=empty,
        )

    def to_conll_ctree(self):
        return "\n".join(
            [
                token.form + "\t" + pseudotag
                for token, pseudotag in zip(self, self.get_ctree_pseudotags())
            ]
        )

    @staticmethod
    def from_cintil(sentence, format_spec):
        return LxSentence.from_primitive_types(
            parse_cintil_sentence(sentence, format_spec),
            default_cintil_format_spec=format_spec,
        )

    @staticmethod
    def from_primitive_types(
        sentence, raw=None, default_cintil_format_spec=None, ctree=None
    ):
        "This method is useful when one needs to send/receive sentences via XML-RPC"
        if isinstance(sentence, list):
            return LxSentence(
                *[LxToken.from_primitive_types(token) for token in sentence],
                raw=raw,
                default_cintil_format_spec=default_cintil_format_spec,
                ctree=ctree,
            )
        if isinstance(sentence, str):
            return LxSentence(
                raw=sentence,
                default_cintil_format_spec=default_cintil_format_spec,
                ctree=ctree,
            )
        raise TypeError("sentence must be a list or a string")

    @staticmethod
    def from_conll(lines, universal=False):
        sentence = lxcommon.conllx.readsent(lines)
        if universal:
            return LxSentence(
                *[
                    LxToken(
                        t.form,
                        ulemma=t.lemma,
                        upos=t.pos,
                        ufeats=t.feats,
                        uparent=t.head,
                        udeprel=t.deprel,
                    )
                    for t in sentence
                ]
            )
        return LxSentence(
            *[
                LxToken(
                    t.form,
                    lemma=t.lemma,
                    pos=t.pos,
                    feats=t.feats,
                    parent=t.head,
                    deprel=t.deprel,
                )
                for t in sentence
            ]
        )

    def to_primitive_types(self, **kwargs):
        "This method is useful when one needs to send/receive sentences via XML-RPC"
        if self.tokenized:
            return [token.to_primitive_types(**kwargs) for token in self]
        return self.raw

    def __repr__(self):
        if not self.tokenized:
            if self.raw:
                return f"LxSentence(raw={self.raw!r})"
            else:
                return "LxSentence()"
        tokens = ", ".join([repr(token) for token in self])
        if self.raw:
            return f"LxSentence({tokens}, raw={self.raw!r})"
        return f"LxSentence({tokens})"

    def copy(self):
        return LxSentence(
            *[token.copy() for token in self],
            raw=self.raw,
            default_cintil_format_spec=self.default_cintil_format_spec,
        )
