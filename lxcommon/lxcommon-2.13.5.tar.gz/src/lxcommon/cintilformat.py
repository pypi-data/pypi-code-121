import logging
import re
import unicodedata

from .utils import recase_as, normalize_text


LOG = logging.getLogger(__name__)


class CintilFormatError(Exception):
    pass


class CintilTokenMissingPOS(CintilFormatError):
    pass


class CintilTokenMissingInfl(CintilFormatError):
    pass


class CintilTokenMissingNE(CintilFormatError):
    pass


class CintilSentenceMissingTag(CintilFormatError):
    pass


class CintilSentenceExtraneousTag(CintilFormatError):
    pass


class CintilParagraphMissingTag(CintilFormatError):
    pass


class CintilParagraphExtraneousTag(CintilFormatError):
    pass


class CintilParagraphExtraneousText(CintilFormatError):
    pass


class CintilExtraneousText(CintilFormatError):
    pass


class CintilFormatSpecError(Exception):
    pass


class CintilFormatSpec:
    def __init__(
        self,
        tokenized=None,
        pos=None,
        morph=None,
        ne=None,
        bracketed=None,
        strict=False,
    ):
        """One or all of tokenized, pos, morph or ne must be given and of type bool.

        If only tokenized is given, it implies pos=False, morph=False and ne=False
        If only pos is given, it implies tokenized=True, morph=False and ne=False
        If only morph is given, it implies tokenized=True, pos=True and ne=False
        If only ne is given, it implies tokenized=True, pos=True and morph=True

        Argument bracketed may be given only when ne=True and defaults to True.

        If strict is given and True, then exceptions will be raised whenever an
        error is found instead of returning the best effort.
        """
        arg_names = ["tokenized", "pos", "morph", "ne"]
        arg_values = (tokenized, pos, morph, ne)
        n_given = 0
        for name, value in zip(arg_names, arg_values):
            if value is not None:
                if not isinstance(value, bool):
                    raise TypeError(f"{name} must be a bool")
                n_given += 1
        if n_given == 1:
            tokenized, pos, morph, ne = {
                # given args: result
                (False, None, None, None): (False, False, False, False),
                (True, None, None, None): (True, False, False, False),
                (None, False, None, None): (True, False, False, False),
                (None, True, None, None): (True, True, False, False),
                (None, None, False, None): (True, True, False, False),
                (None, None, True, None): (True, True, True, False),
                (None, None, None, False): (True, True, True, False),
                (None, None, None, True): (True, True, True, True),
            }[arg_values]
        elif n_given == len(arg_names):
            # all were given; let's check their consistency
            # (by checking that arg_values are sorted)
            for lname, lvalue, rname, rvalue in zip(
                arg_names[:-1], arg_values[:-1], arg_names[1:], arg_values[1:]
            ):
                if lvalue > rvalue:
                    raise CintilFormatSpecError(
                        f"invalid format spec: {rname} cannot be True"
                        f" if {lname} is False"
                    )
        else:  # either none or more than one but not all arguments were given
            raise CintilFormatSpecError(
                "either one or all of tokenized, pos, morph or ne"
                " must be given and of type bool"
            )
        if ne is True:
            if bracketed is not None and not isinstance(bracketed, bool):
                raise TypeError("bracketed must be of type bool")
            bracketed = bracketed or bracketed is None
        elif bracketed is not None:
            raise CintilFormatSpecError("bracketed may be given only if ne is True")
        super(CintilFormatSpec, self).__setattr__("tokenized", tokenized)
        super(CintilFormatSpec, self).__setattr__("pos", pos)
        super(CintilFormatSpec, self).__setattr__("morph", morph)
        super(CintilFormatSpec, self).__setattr__("ne", ne)
        super(CintilFormatSpec, self).__setattr__("bracketed", bracketed)
        super(CintilFormatSpec, self).__setattr__("strict", strict)

    def __setattr__(self, name, value):
        raise CintilFormatSpecError("CintilFormatSpec objects are immutable")

    def __repr__(self):
        return (
            f"CintilFormatSpec(tokenized={self.tokenized}, pos={self.pos}, "
            f"morph={self.morph}, ne={self.ne}, bracketed={self.bracketed})"
        )

    def __eq__(self, other):
        if not isinstance(other, CintilFormatSpec):
            raise TypeError("other must be an instance of CintilFormatSpec")
        return (
            self.tokenized == other.tokenized
            and self.pos == other.pos
            and self.morph == other.morph
            and self.ne == other.ne
            and self.bracketed == other.bracketed
        )


def _maybeatag(form):
    # this may give false positives but it's better to be on the safe side
    return form.startswith("<") and form.endswith(">")


_remainder_pat = "(?P<remainder>.*)"


_ne_pat = r"(?P<ne>O|[BI]-[A-Z]+)"
_match_ne = re.compile(f"^{_remainder_pat}/{_ne_pat}$").match
_match_bracketed_ne = re.compile(f"^{_remainder_pat}\\[{_ne_pat}\\]$").match


def _parse_bracketed_ne(token):
    m = _match_bracketed_ne(token)
    if m:
        return m.group("remainder"), m.group("ne")
    return token, None


def _parse_ne(token):
    m = _match_ne(token)
    if m:
        return m.group("remainder"), m.group("ne")
    return token, None


# TODO: write a regex that matches exactly the set of possible inflection flags
# A question mark (?) is inserted by vlemma when the infl is not known
# apparently, two question marks are also allowed as in Monsenhor/STT#??
_infl_pat = r"(?P<infl>[?a-zA-Z1-9]+(?:-[?a-zA-Z1-9]+)*)"
_match_infl = re.compile(f"^{_remainder_pat}#{_infl_pat}$").match


def _parse_infl(token):
    m = _match_infl(token)
    if m:
        return m.group("remainder"), m.group("infl")
    if token.endswith("#"):
        # smelly case: inflection tags separator present but no tags given
        # let it pass as if no separator and no tags were present;
        token = token[:-1]
    return token, None


# TODO: write a regex that matches exactly the set of possible POS tags
_pos_pat = r"(?P<pos>@?[A-Z]+|L[A-Z]+[1-9]+)"
_match_pos = re.compile(f"^{_remainder_pat}/{_pos_pat}$").match


def _parse_pos(token):
    m = _match_pos(token)
    if m:
        return m.group("remainder"), m.group("pos")
    return token, None


# A lemma is either
#   - question mark (?) (sometimes inserted by vlemma when the lemma is not known)
#   - a sequence of any characters except slash ([^/]+)
_single_lemma_pat = r"(?:\?|[^/]+|@URL|@EMAIL)"
_lemma_pat = r"(?P<lemma>" + _single_lemma_pat + "(?:," + _single_lemma_pat + ")*)"
_match_lemma = re.compile(f"^{_remainder_pat}/{_lemma_pat}$").match


def _parse_lemma(token):
    m = _match_lemma(token)
    if m:
        return m.group("remainder"), m.group("lemma")
    return token, None


def _is_punct(form):
    return all(unicodedata.category(c)[0] == "P" for c in form)


def _parse_form(form):
    if form.startswith("\\*"):
        form = form[2:]
        space = "L"
    else:
        space = None
    if form.endswith("*/"):
        space = "LR" if space == "L" else "R"
        form = form[:-2]
    if space is None:
        if _is_punct(form):
            # puctuation has no spaces unless we say otherwise (space not None)
            space = ""
        else:
            # every token that is neither punctuation nor symbol has spaces on both
            # sides unless they are prefixed with a hyphen - or suffixed with an
            # underscore_
            space = "L" if not form.startswith("-") else ""
            space += "R" if not form.endswith("_") else ""
    return form, space


def parse_cintil_token(token, format_spec):
    """
    Parses a token in CINTIL format into a dictionary.
    Notes:
        format_spec.pos=False implies
            format_spec.morph=False and
            format_spec.ne=False
        format_spec.morph=False implies
            format_spec.ne=False

    Admissible formats:

        word
            format_spec.pos=False, format_spec.morph=False, format_spec.ne=False

        word/pos
            format_spec.pos=True, format_spec.morph=False, format_spec.ne=False

        word/lemma/pos#infl
            format_spec.pos=True, format_spec.morph=True, format_spec.ne=False

        word/pos#infl   (function words)
            format_spec.pos=True, format_spec.morph=True, format_spec.ne=False

        word/lemma/pos#infl/ne
            format_spec.pos=True, format_spec.morph=True, format_spec.ne=True

        word/lemma/pos#infl[ne]
            format_spec.pos=True, format_spec.morph=True, format_spec.ne=True,
            format_spec.bracketed=True

    """
    if not isinstance(token, str):
        raise TypeError("token must be a string")
    if not isinstance(format_spec, CintilFormatSpec):
        raise TypeError("format_spec must be an instance of CintilFormatSpec")

    token = normalize_text(token)

    if _maybeatag(token):
        return dict(form=token)

    d = dict()
    remainder = token

    if format_spec.ne:
        if format_spec.bracketed:
            remainder, ne = _parse_bracketed_ne(remainder)
        else:
            remainder, ne = _parse_ne(remainder)
        if not ne:
            LOG.warning(f"missing NE tag in token {token!r}")
            if format_spec.strict:
                raise CintilTokenMissingNE(f"missing NE tag in token {token!r}")
        d["ne"] = ne

    if format_spec.morph:
        remainder, infl = _parse_infl(remainder)
        if infl:
            d["infl"] = infl
        remainder, pos = _parse_pos(remainder)
        if not pos:
            LOG.warning(f"missing pos tag in token {token!r}")
            if format_spec.strict:
                raise CintilTokenMissingPOS(f"missing POS tag in token {token!r}")
        d["pos"] = pos
        remainder, lemma = _parse_lemma(remainder)
        if lemma:
            d["lemma"] = lemma
            if infl is None and pos != "EADR":
                LOG.warning(f"missing inflection tags in token {token!r}")
                if format_spec.strict:
                    raise CintilTokenMissingInfl(
                        f"missing inflection tags in token {token!r}"
                    )
            # We should always have inflection flags if we have a lemma, except
            #  if pos is EADR.
            # However, it is perfectly normal to have inflection tags without lemma.
            # for example: o/DA#ms

    elif format_spec.pos:
        remainder, pos = _parse_pos(remainder)
        if not pos:
            LOG.warning(f"missing POS tag in token {token!r}")
            if format_spec.strict:
                raise CintilTokenMissingPOS(f"missing POS tag in token {token!r}")
        d["pos"] = pos

    form, space = _parse_form(remainder)
    d["form"] = form
    d["space"] = space

    return d


def parse_cintil_sentence(sentence, format_spec):
    """Parses a sentence in CINTIL format.

    Checks that the sentence is wrapped with <s> and </s> tags and raises
    CintilFormatError if it is not.
    If format_spec.tokenized is False this function will return the sentence
    as a single string without <s> and </s> tags.
    If format_spec.tokenized is True this function will split the sentence on
    whitespace, invoke lxcommon.cintilformat.parse_token for each token, and
    return a list of dictionaries.

    """
    if not isinstance(sentence, str):
        raise TypeError("sentence must be a string")
    if not isinstance(format_spec, CintilFormatSpec):
        raise TypeError("format_spec must be an instance of CintilFormatSpec")
    original_sentence, sentence = sentence, sentence.strip()
    sentence = sentence.replace("<S>", "<s>").replace("</S>", "</s>")
    if not sentence.startswith("<s>") or not sentence.endswith("</s>"):
        msg = f"sentence is not wrapped within <s> and </s> tags: {original_sentence!r}"
        LOG.warning(msg)
        if format_spec.strict:
            raise CintilSentenceMissingTag(msg)
        # else just assume that this is a sentence (best effort)
    if sentence.startswith("<s>"):
        sentence = sentence[3:].lstrip()
    if sentence.endswith("</s>"):
        sentence = sentence[:-4].rstrip()
    if "<s>" in sentence or "</s>" in sentence:
        msg = f"sentence contains multiple <s> or </s> tags: {original_sentence!r}"
        LOG.warning(msg)
        if format_spec.strict:
            raise CintilSentenceExtraneousTag(msg)
        else:
            # delete extraneous tags (best effort)
            sentence = sentence.replace("<s>", "").replace("</s>", "")
    if format_spec.tokenized:
        sentence = [
            parse_cintil_token(token, format_spec) for token in sentence.split()
        ]
        for previous_token, token in zip(sentence, sentence[1:]):
            if "R" not in previous_token["space"] and "L" in token["space"]:
                token["space"] = token["space"].replace("L", "")
            elif "L" not in token["space"] and "R" in previous_token["space"]:
                previous_token["space"] = previous_token["space"].replace("R", "")
    return sentence


def parse_cintil_paragraph(paragraph, format_spec):
    """Parses a paragraph in CINTIL format.

    Checks that the paragraph is wrapped with <p> and </p> tags and raises
    CintilFormatError if it is not.
    If format_spec.tokenized is False this function will return the paragraph
    as a list of strings, one for each sentence in the paragraph.
    If format_spec.tokenized is True this function will return a list of lists
    of dictionaries.  Each dictionary represents a token and each list of
    dictionaries represents a sentence.

    """
    if not isinstance(paragraph, str):
        raise TypeError("paragraph must be a string")
    if not isinstance(format_spec, CintilFormatSpec):
        raise TypeError("format_spec must be an instance of CintilFormatSpec")
    original_paragraph, paragraph = paragraph, paragraph.strip()
    paragraph = (
        paragraph.replace("<P>", "<p>")
        .replace("</P>", "</p>")
        .replace("<S>", "<s>")
        .replace("</S>", "</s>")
    )
    if not paragraph.startswith("<p>") or not paragraph.endswith("</p>"):
        msg = (
            f"paragraph is not wrapped within <p> and </p> tags: {original_paragraph!r}"
        )
        LOG.warning(msg)
        if format_spec.strict:
            raise CintilParagraphMissingTag(msg)
        # else just assume that this is a paragraph (best effort)
    if paragraph.startswith("<p>"):
        paragraph = paragraph[3:].lstrip()
    if paragraph.endswith("</p>"):
        paragraph = paragraph[:-4].rstrip()
    if "<p>" in paragraph or "</p>" in paragraph:
        msg = f"paragraph contains multiple <p> or </p> tags: {original_paragraph!r}"
        LOG.warning(msg)
        if format_spec.strict:
            raise CintilParagraphExtraneousTag(msg)
        else:
            # delete extraneous tags (best effort)
            paragraph = paragraph.replace("<p>", "").replace("</p>", "")

    sentences = []
    warning_shown = False
    while paragraph:
        end = paragraph.find("</s>")
        if not paragraph.startswith("<s>") or end == -1:
            msg = (
                "paragraph contains text outside <s> and </s> tags:"
                f" {original_paragraph!r}"
            )
            if not warning_shown:
                LOG.warning(msg)
                warning_shown = True
            if format_spec.strict:
                raise CintilParagraphExtraneousText(msg)
            if end == -1:  # no </s>, let's try to split on next <s> (best effort)
                if paragraph.startswith("<s>"):
                    # remove "<s>" from begining of paragraph:
                    paragraph = paragraph[3:]
                # consider the next "<s>" as the marker of end of this sentence:
                end = paragraph.find("<s>")
                if end == -1:
                    sentence, paragraph = paragraph, ""
                else:
                    sentence, paragraph = paragraph[:end].strip(), paragraph[end:]
                continue
            # else this means paragraph does not start with <s> but end != -1
        sentence, paragraph = paragraph[: end + 4], paragraph[end + 4 :].lstrip()
        sentences.append(parse_cintil_sentence(sentence, format_spec))
    return sentences


def format_cintil_token(token, format_spec):
    "Formats a token in CINTIL format."
    if not isinstance(token, dict):
        raise TypeError("token must be a dict")
    if not isinstance(format_spec, CintilFormatSpec):
        raise TypeError("format_spec must be an instance of CintilFormatSpec")

    form = recase_as(token["form"], token["raw"]) if "raw" in token else token["form"]
    form = normalize_text(form)
    if _maybeatag(form):
        return form

    cintil_token = form

    space = token.get("space")
    if _is_punct(form) and space:
        if "L" in space:
            cintil_token = r"\*" + cintil_token
        if "R" in space:
            cintil_token += "*/"

    if not format_spec.pos:
        return cintil_token

    lemma = token.get("lemma") if format_spec.morph else None
    if lemma:
        lemma = normalize_text(lemma)
        cintil_token += f"/{lemma}"

    pos = token.get("pos")
    cintil_token += f"/{pos}"

    infl = None
    if format_spec.morph:
        infl = token.get("feats", token.get("infl", None))
    if infl:
        cintil_token += f"#{infl}"

    if format_spec.ne:
        ne = token.get("ne") or token.get("ne_rb")
        cintil_token += f"[{ne}]" if format_spec.bracketed else f"/{ne}"

    return cintil_token


def format_cintil_sentence(sentence, format_spec):
    if not isinstance(format_spec, CintilFormatSpec):
        raise TypeError("format_spec must be an instance of CintilFormatSpec")
    if not format_spec.tokenized:
        if not isinstance(sentence, str):
            raise TypeError(
                "sentence must be a string (because format_spec.tokenized is False)"
            )
        sentence = sentence.strip()
        return f"<s> {sentence} </s>" if sentence else "<s> </s>"
    if not isinstance(sentence, (list, tuple)):
        raise TypeError("sentence must be an instance of list or tuple")
    if not sentence:
        return "<s> </s>"
    cintil_tokens = [format_cintil_token(token, format_spec) for token in sentence]
    return "<s> " + " ".join(cintil_tokens) + " </s>"


def format_cintil_paragraph(paragraph, format_spec):
    if not isinstance(paragraph, (list, tuple)):
        raise TypeError("paragraph must be an instance of list or tuple")
    if not isinstance(format_spec, CintilFormatSpec):
        raise TypeError("format_spec must be an instance of CintilFormatSpec")
    if not paragraph:
        return "<p> </p>"
    cintil_sentences = [
        format_cintil_sentence(sentence, format_spec) for sentence in paragraph
    ]
    return "<p> " + "\n".join(cintil_sentences) + " </p>"


def _get_close_p_pos(s):
    pos = s.find("</p>")
    if pos == -1:
        return None
    return pos + 4


def read_cintil_paragraphs(input_file, format_spec=None):
    paragraph_lines = []  # start reading new paragraph
    for linenum, line in enumerate(input_file, start=1):
        line = line.strip()
        if not line:  # skip empty lines
            continue
        if paragraph_lines:  # we are inside a paragraph
            close_p_pos = _get_close_p_pos(line)
            if close_p_pos is None:  # paragraph does not end on this line
                paragraph_lines.append(line)
                continue  # onto next line
            # else paragraph ends on close_p_pos
            paragraph_lines.append(line[:close_p_pos])
            paragraph = " ".join(paragraph_lines)
            yield parse_cintil_paragraph(
                paragraph, format_spec
            ) if format_spec else paragraph
            paragraph_lines = []  # start reading new paragraph from line[close_p_pos:]
            line = line[close_p_pos:].lstrip()
            if not line:
                continue  # onto next line
            # else fall through and start reading new paragraph from the
            # remainder of the current line
        while line:
            # handle the unusual situation of one or more <p> ... </p> in a single line
            if not line.startswith("<p>"):  # left space has been stripped above
                raise CintilExtraneousText(
                    f"line {linenum} has text outside <p> and </p> tags"
                )
            close_p_pos = _get_close_p_pos(line)
            if close_p_pos is None:
                paragraph_lines.append(line)
                # whole (remainder of) line is part of paragraph
                break  # nothing left to do with this line
            paragraph = line[:close_p_pos]
            yield parse_cintil_paragraph(
                paragraph, format_spec
            ) if format_spec else paragraph
            line = line[
                close_p_pos:
            ].strip()  # will continue the while loop until line is empty
    if paragraph_lines:
        raise CintilParagraphMissingTag("unclosed paragraph at the end of file")


def write_cintil_paragraphs(paragraphs, output_file, format_spec):
    for paragraph in paragraphs:
        print(format_cintil_paragraph(paragraph, format_spec), file=output_file)
