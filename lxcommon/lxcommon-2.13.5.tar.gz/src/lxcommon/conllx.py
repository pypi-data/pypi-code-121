"""Module for reading and writing CONLL-X format

 Luís Gomes <luis.gomes@di.fc.ul.pt>, <luismsgomes@gmail.com>

 Copyright NLX-Group, Universidade de Lisboa, 2015-2022


The following text is adapted from http://ilk.uvt.nl/conll/:

Files contain sentences separated by a blank line.
A sentence consists of one or tokens, each one starting on a new line.
A token consists of ten fields described in the table below. Fields are
 separated by a single tab character. Space/blank characters are not allowed in
 within fields.
All files will contains these ten fields, although only the ID, FORM, CPOSTAG,
 POSTAG, HEAD and DEPREL columns are guaranteed to contain non-dummy (i.e.
 non-underscore) values.

Fields:
1   ID      Token counter, starting at 1 for each new sentence.
2   FORM    Word form or punctuation symbol.
3   LEMMA   Lemma or stem (depending on particular data set) of word form, or an
            underscore if not available.
4   CPOSTAG Coarse-grained part-of-speech tag, where tagset depends on the
            language.
5   POSTAG  Fine-grained part-of-speech tag, where the tagset depends on the
            language, or identical to the coarse-grained part-of-speech tag if
            not available.
6   FEATS   Unordered set of syntactic and/or morphological features (depending
            on the particular language), separated by a vertical bar (|), or an
            underscore if not available.
7   HEAD    Head of the current token, which is either a value of ID or zero
            ('0'). Note that depending on the original treebank annotation,
            there may be multiple tokens with an ID of zero.
8   DEPREL  Dependency relation to the HEAD. The set of dependency relations
            depends on the particular language. Note that depending on the
            original treebank annotation, the dependency relation may be
            meaningfull or simply 'ROOT'.
9   PHEAD   Projective head of current token, which is either a value of ID or
            zero ('0'), or an underscore if not available. Note that depending
            on the original treebank annotation, there may be multiple tokens an
            with ID of zero. The dependency structure resulting from the PHEAD
            column is guaranteed to be projective (but is not available for all
            languages), whereas the structures resulting from the HEAD column
            will be non-projective for some sentences of some languages (but is
            always available).
10  PDEPREL Dependency relation to the PHEAD, or an underscore if not available.
            The set of dependency relations depends on the particular language.
            Note that depending on the original treebank annotation, the
            dependency relation may be meaningfull or simply 'ROOT'.
"""

import sys


EMPTY_MARKERS = (
    "_",  # this is the standard marker for no value
    "-",
    "",
)


class ConllxToken:
    __slots__ = [  # field
        "tokid",  # 1
        "form",  # 2
        "lemma",  # 3
        "cpos",  # 4
        "pos",  # 5
        "feats",  # 6
        "head",  # 7
        "deprel",  # 8
        "phead",  # 9
        "pdeprel",  # 10
    ]

    def __init__(self, *args, **kwargs):
        """Creates a token from str, tuple or dict"""
        if args:
            if len(args) == 1:
                if isinstance(args[0], str):
                    self._init_from_str(args[0])
                elif isinstance(args[0], tuple):
                    self._init_from_seq(args[0])
                elif isinstance(args[0], dict):
                    self._init_from_dict(args[0])
                else:
                    raise ValueError("Unexpected argument type: " + type(args[0]))
            else:
                assert len(args) == len(ConllxToken.__slots__)
                self._init_from_seq(args)
        elif kwargs:
            self._init_from_dict(kwargs)
        else:
            raise ValueError("Missing argument(s)")

    def __str__(self):
        return self.asstr()

    def __repr__(self):
        return f"ConllxToken{self.astuple()!r}"

    def asstr(self):
        return "\t".join(
            [EMPTY_MARKERS[0] if v is None else str(v) for v in self.astuple()]
        )

    def astuple(self):
        return tuple(getattr(self, attr) for attr in ConllxToken.__slots__)

    def asdict(self):
        return {attr: getattr(self, attr) for attr in ConllxToken.__slots__}

    def _init_from_str(self, arg):
        fields = arg.split("\t")
        assert len(fields) == 10
        try:
            fields = tuple(
                None
                if field in EMPTY_MARKERS and fieldnum != 2  # form
                else int(field)
                if fieldnum in {1, 7, 9}  # tokid, head, phead
                else field
                for fieldnum, field in enumerate(fields, start=1)
            )
        except Exception as ex:
            print("Invalid line:", arg, file=sys.stderr)
            print("Exception:", ex, file=sys.stderr)
            raise ex
        self._init_from_seq(fields)

    def _init_from_seq(self, arg):
        for attr, v in zip(ConllxToken.__slots__, arg):
            setattr(self, attr, v)

    def _init_from_dict(self, arg):
        for attr in ConllxToken.__slots__:
            setattr(self, attr, arg.get(attr, None))


def readsent(f):
    sent = []
    for line in f:
        line = line.rstrip("\n")
        if line.startswith("#"):
            continue
        if line:
            sent.append(ConllxToken(line))
        elif len(sent) > 0:
            break
    return sent


def writesent(f, sent, flush=True):
    assert isinstance(sent, list) and len(sent) > 0
    for token in sent:
        assert isinstance(token, ConllxToken)
        print(str(token), file=f)
    print(flush=flush, file=f)


def read(f):
    while True:
        sent = readsent(f)
        if sent:
            yield sent
        else:
            return


def write(f, sents, flush=True):
    for sent in sents:
        writesent(f, sent, flush=flush)


def fix_roots(sent):
    rootid = None
    assert all(isinstance(token, ConllxToken) for token in sent)
    for tok in sent:
        if tok.head == 0 and tok.deprel == "ROOT":
            rootid = tok.tokid
            break
    assert rootid is not None
    for tok in sent:
        if tok.tokid != rootid and tok.head == 0:
            tok.head = rootid
            if tok.phead is not None:
                tok.phead = tok.head
            if tok.deprel == "ROOT":
                tok.deprel = "DEP"
                if tok.pdeprel is not None:
                    tok.pdeprel = tok.deprel
    return sent


__all__ = ["ConllxToken", "readsent", "writesent", "read", "write", "fix_roots"]
