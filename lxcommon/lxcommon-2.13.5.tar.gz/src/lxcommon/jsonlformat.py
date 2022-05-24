"""This module implements the JSONL (one JSON object per Line) text annotation format.
 This is the preferred future-proof format.

 Each line contains a sentence, which is a JSON object containing the following fields:

 - tokens (mandatory/list of strings): tokens that compose the sentence
 - lemmas (optional/list of strings): lemma for each token
 - ulemmas (optional/list of strings): universal lemma for each token
 - pos_tags (optional/list of strings): part-of-speech tag for each token
 - upos_tags (optional/list of strings): universal part-of-speech tag for each token
 - ne_tags (optional/list of strings): named entity tag for each token
 - feats (optional/list of strings): morphological/inflection features for each token
 - ufeats (optional/list of strings): universal morphological/inflection features
                                      for each token
 - dep_heads (optional/list of ints): dependency relation head for each token
 - dep_rels (optional/list of strings): dependency relation tag for each token
 - udep_heads (optional/list of ints): universal dependency relation head for each
                                      token
 - udep_rels (optional/list of strings): universal dependency relation tag for each
                                      token
 - spaces (optional/string): one character for each token indicating spacing:
                              L=Left, R=Right, B=Both, N=None
 - par_id (optiona/string): the identifier of the paragraph to which this sentence
                            belongs
 - raw_sent (optional/string): the original plain-text sentence before tokenization
 - ctree (optional/string): constituency tree in parentheses format
 - sent_id (optional/string/int): sentence identifier
 - par_id (optional/string/int): paragraph identifier
"""

import json
import logging

from .lxparagraph import LxParagraph
from .lxsentence import LxSentence
from .lxtoken import LxToken

LOG = logging.getLogger(__name__)

JSONSENTENCE_LXTOKEN_MAPPING = [
    # (jsonsentence key, lxtoken attr)
    ("pos_tags", "pos"),
    ("upos_tags", "upos"),
    ("lemmas", "lemma"),
    ("ulemmas", "ulemma"),
    ("spaces", "space"),
    ("ne_tags", "ne"),
    ("ne_rb_tags", "ne_rb"),
    ("feats", "feats"),
    ("ufeats", "ufeats"),
    ("dep_heads", "parent"),
    ("dep_rels", "deprel"),
    ("udep_heads", "uparent"),
    ("udep_rels", "udeprel"),
]


def jsonsentence_to_lxsentence(jsonsentence):
    lxtokens = [LxToken(token) for token in jsonsentence["tokens"]]
    for jsonsentence_field, lxtoken_attr in JSONSENTENCE_LXTOKEN_MAPPING:
        if jsonsentence_field in jsonsentence:
            for value, lxtoken in zip(jsonsentence[jsonsentence_field], lxtokens):
                setattr(lxtoken, lxtoken_attr, value)
    raw = jsonsentence.get("raw_sent", None)
    sent_id = jsonsentence.get("sent_id", None)
    par_id = jsonsentence.get("par_id", None)
    ctree = jsonsentence.get("ctree", None)
    lxsentence = LxSentence(
        *lxtokens, raw=raw, ctree=ctree, sent_id=sent_id, par_id=par_id
    )
    return lxsentence


def lxsentence_to_jsonsentence(lxsentence):
    jsonsentence = dict(tokens=[token.form for token in lxsentence])
    for key, attr in JSONSENTENCE_LXTOKEN_MAPPING:
        values = [
            getattr(token, attr) if hasattr(token, attr) else None
            for token in lxsentence
        ]
        if any(value is not None for value in values):
            jsonsentence[key] = values
    for attr in ["ctree", "sent_id", "par_id"]:
        value = getattr(lxsentence, attr)
        if value is not None:
            jsonsentence[attr] = value
    return jsonsentence


def read_jsonl_sentences(input_file, ignore_errors=False):
    for linenum, line in enumerate(input_file, start=1):
        try:
            yield jsonsentence_to_lxsentence(json.loads(line))
        except json.JSONDecodeError:
            LOG.exception(f"invalid JSON object in line {linenum}")
            if ignore_errors:
                continue
            raise


def read_jsonl_paragraphs(input_file, ignore_errors=False):
    par, par_id = [], None
    for sentence in read_jsonl_sentences(input_file, ignore_errors):
        if hasattr(sentence, "par_id"):
            if par:
                if par_id is not None and par_id == sentence.par_id:
                    par.append(sentence)
                else:
                    yield LxParagraph(*par, par_id=par_id)
                    par, par_id = [sentence], sentence.par_id
            else:
                par.append(sentence)
        else:
            if par:
                yield LxParagraph(*par, par_id=par_id)
                par, par_id = [], None
            yield LxParagraph(sentence)
    if par:
        yield LxParagraph(*par, par_id=par_id)


def write_jsonl_sentence(lxsentence, output_file):
    jsonsentence = lxsentence_to_jsonsentence(lxsentence)
    print(json.dumps(jsonsentence), file=output_file)


def write_jsonl_paragraph(lxparagraph, output_file):
    for lxsentence in lxparagraph:
        write_jsonl_sentence(lxsentence, output_file)


def write_jsonl_paragraphs(lxparagraphs, output_file):
    for lxparagraph in lxparagraphs:
        write_jsonl_paragraph(lxparagraph, output_file)
