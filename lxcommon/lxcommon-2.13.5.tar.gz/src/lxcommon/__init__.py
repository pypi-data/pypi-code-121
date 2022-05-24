"""
Luís Gomes <luis.gomes@di.fc.ul.pt>, <luismsgomes@gmail.com>

Copyright NLX-Group, Universidade de Lisboa, 2015-2020
"""

__version__ = "2.13.5"


from .cintilformat import (  # noqa: F401
    CintilFormatError,
    CintilFormatSpec,
    CintilTokenMissingPOS,
    CintilTokenMissingInfl,
    CintilTokenMissingNE,
    CintilSentenceMissingTag,
    CintilSentenceExtraneousTag,
    CintilParagraphMissingTag,
    CintilParagraphExtraneousTag,
    CintilParagraphExtraneousText,
    format_cintil_paragraph,
    format_cintil_sentence,
    format_cintil_token,
    parse_cintil_paragraph,
    parse_cintil_sentence,
    parse_cintil_token,
    read_cintil_paragraphs,
    write_cintil_paragraphs,
)
from .conllformat import format_conll_sentence  # noqa: F401
from .jsonlformat import (  # noqa: F401
    jsonsentence_to_lxsentence,
    lxsentence_to_jsonsentence,
    read_jsonl_paragraphs,
    read_jsonl_sentences,
    write_jsonl_paragraphs,
    write_jsonl_paragraph,
    write_jsonl_sentence,
)
from .lxtoken import LxToken  # noqa: F401
from .lxsentence import LxSentence  # noqa: F401
from .lxparagraph import LxParagraph  # noqa: F401
from .contractions import CONTRACTIONS  # noqa: F401
from .utils import normalize_unicode, normalize_text, recase_as  # noqa: F401
