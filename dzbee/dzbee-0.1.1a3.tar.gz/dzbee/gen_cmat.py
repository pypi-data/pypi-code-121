"""Gen cmat for en/zh text."""
# pylint: disable=

from typing import List, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from fastlid import fastlid
from logzero import logger
from fast_scores import fast_scores
from fast_scores.process_en import process_en
from fast_scores.en2zh import en2zh
from fast_scores.process_zh import process_zh

# fix on en/zh, warn if confidence too low
fastlid.set_languages = ["en", "zh"]


def gen_cmat(
    text1: List[str],
    text2: List[str],
    model: Optional[TfidfVectorizer] = None,
) -> np.ndarray:
    """Gen corr matrix for en/zh texts."""
    # logger.debug("enter gen_cmat")
    if isinstance(text1, str):
        text1 = [text1]
    if isinstance(text2, str):
        text1 = [text2]
    lang1, conf1 = fastlid("\n".join(text1))
    lang2, conf2 = fastlid("\n".join(text2))

    # ic(lang1)
    # ic(lang2)

    if conf1 < 0.1:
        logger.warning(" text1 dected as %s, but confidence too low: %s, make sure you supply english or chinese texts", lang1, conf1)

    if conf2 < 0.1:
        logger.warning(" text2 dected as %s, but confidence too low: %s, make sure you supply english or chinese texts", lang2, conf2)

    if lang1 in ["en"] and lang2 in ["en"]:
        logger.warning("Both texts are en...are you sure you supplied the correct files?")

    if lang1 in ["zh"] and lang2 in ["zh"]:
        logger.warning("Both texts are zh...are you you supplied the correct files?")

    logger.debug("gen text1a text2a")
    # _ = """
    if lang1 in ["en"] and lang2 in ["en"]:
        text1a = en2zh(process_en(text1))
        text2a = en2zh(process_en(text2))
    elif lang1 in ["en"] and lang2 in ["zh"]:
        text1a = en2zh(process_en(text1))
        text2a = process_zh(text2)
    elif lang1 in ["zh"] and lang2 in ["en"]:
        text1a = process_zh(text1)
        text2a = en2zh(process_en(text2))
    # if lang1 in ["zh"] and lang2 in ["zh"]:
    else:
        text1a = process_zh(text1)
        text2a = process_zh(text2)
    # """

    # text1a = globals()["process_" + lang1](text1)
    # text2a = globals()["process_" + lang2](text2)

    logger.debug("execute fast_scores")
    _ = fast_scores(text1a, text2a, model=model)

    return _


_ = """

cmat = gen_cmat(en, zh)
aset = cmat2aset(cmat)

i = -1

i += 1
i, en[aset[i][0]] if isinstance(aset[i][0], int) else "", zh[aset[i][1]] if isinstance
(
    aset[i][1], int
) else "", aset[i][2]

"""
