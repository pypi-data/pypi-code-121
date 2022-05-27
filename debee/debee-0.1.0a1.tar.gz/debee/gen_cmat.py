"""Gen cmat for de/en text."""
# pylint: disable=

from typing import List, Optional

import numpy as np

# from fast_scores.en2zh import en2zh
# from json_de2zh.de2zh import de2zh
from de2en import de2en
from fast_scores import fast_scores

# from fast_scores.process_zh import process_zh
from fast_scores.process_en import process_en
from fastlid import fastlid
from json_de2zh.process_de import process_de
from logzero import logger
from sklearn.feature_extraction.text import TfidfVectorizer

from debee.remove_punct import remove_punct

# from json_de2zh.process_zh import process_zh

# from fast_scores.process_de import process_de

# fix on de/zh, warn if confidence too low
# fastlid.set_languages = ["de", "zh"]  # need to move inside gen_cmat


def gen_cmat(
    text1: List[str],
    text2: List[str],
    model: Optional[TfidfVectorizer] = None,
    remove_punctuation=True,  # should incorpoerate into process_en
) -> np.ndarray:
    """Gen corr matrix for de/en texts.

    Args:
        text1: typically '''...''' splitlines()
        text2: typically '''...''' splitlines()

    text1 = 'this is a test'
    text2 = 'another test'
    """
    # logger.debug("enter gen_cmat")
    fastlid.set_languages = ["de", "en"]  # bug fix
    if isinstance(text1, str):
        text1 = [text1]
    if isinstance(text2, str):
        text1 = [text2]
    lang1, conf1 = fastlid("\n".join(text1))
    lang2, conf2 = fastlid("\n".join(text2))

    # ic(lang1)
    # ic(lang2)

    if conf1 < 0.1:
        logger.warning(
            " text1 dected as %s, but confidence too low: %s, make sure you supply english or german texts",
            lang1,
            conf1,
        )

    if conf2 < 0.1:
        logger.warning(
            " text2 dected as %s, but confidence too low: %s, make sure you supply english or german texts",
            lang2,
            conf2,
        )

    if lang1 in ["de"] and lang2 in ["de"]:
        logger.warning(
            "Both texts are de...are you sure you supplied the correct files?"
        )

    if lang1 in ["en"] and lang2 in ["en"]:
        logger.warning(
            "Both texts are en...are you sure you supplied the correct files?"
        )

    def tfunc(text):
        """Handle text"""
        _ = remove_punct(text)  # to make pyright happy
        if isinstance(_, str):
            text = [_]
        else:
            text = _[:]
        return text

    logger.debug("gen text1a text2a")
    # _ = """
    if lang1 in ["de"] and lang2 in ["de"]:
        text1a = de2en(process_de(text1))
        text2a = de2en(process_de(text2))
    elif lang1 in ["de"] and lang2 in ["en"]:
        text1a = de2en(process_de(text1))
        if remove_punctuation:
            text2 = tfunc(text2)
        text2a = [" ".join(elm) for elm in process_en(text2)]
    elif lang1 in ["en"] and lang2 in ["de"]:
        if remove_punctuation:
            # text1 = remove_punct(text1)
            text1 = tfunc(text1)
        text1a = [" ".join(elm) for elm in process_en(text1)]
        text2a = de2en(process_de(text2))
    # if lang1 in ["en"] and lang2 in ["en"]:
    else:
        if remove_punctuation:
            # text1 = remove_punct(text1)
            # text2 = remove_punct(text2)
            text1 = tfunc(text1)
            text2 = tfunc(text2)

        text1a = [" ".join(elm) for elm in process_en(text1)]
        text2a = [" ".join(elm) for elm in process_en(text2)]
    # """

    # text1a = globals()["process_" + lang1](text1)
    # text2a = globals()["process_" + lang2](text2)

    logger.debug("execute fast_scores")
    _ = fast_scores(text1a, text2a, model=model)

    return _


_ = """

cmat = gen_cmat(en, zh)
cmat = gen_cmat(en, de)

aset = cmat2aset(cmat)

i = -1

i += 1
i, en[aset[i][0]] if isinstance(aset[i][0], int) else "", zh[aset[i][1]] if isinstance
(
    aset[i][1], int
) else "", aset[i][2]

"""
