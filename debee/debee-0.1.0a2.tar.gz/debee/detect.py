"""Detect language via polyglot and fastlid."""
# pylint: disable=

from typing import Any, Callable, List, Optional

import polyglot.detect.base
from fastlid import fastlid
from logzero import logger
from polyglot.detect.base import UnknownLanguage
from polyglot.text import Detector

polyglot.detect.base.logger.setLevel("ERROR")


def with_func_attrs(**attrs: Any) -> Callable:
    """Define func_attrs."""

    def with_attrs(fct: Callable) -> Callable:
        for key, val in attrs.items():
            setattr(fct, key, val)
        return fct

    return with_attrs


# @with_func_attrs(set_languages=None)
# def detect(text: str) -> str:
def detect(text: str, set_languages: Optional[List[str]] = None) -> str:
    """Detect language via polyglot and fastlid.

    check first with fastlid, if conf < 0.3, check with polyglot.text.Detector

    Alternative in detec_alt.py
    """
    # if not text.strip(): return "en"
    fastlid.set_languages = set_languages
    lang, conf = fastlid(text)
    detect.lang_conf = lang, conf
    if conf >= 0.3 or lang in ["zh"]:
        return lang

    try:
        langs = [(elm.code[:2], elm.confidence) for elm in Detector(text).languages]
        detect.lang_conf = langs
        # lang, conf = _[0]
    except UnknownLanguage:
        if set_languages is None:
            def_lang = "en"
        else:
            # def_lang = set_languages[-1]
            def_lang = set_languages[0]
        logger.warning(
            " UnknownLanguage exception: probably snippet too short, setting to %s",
            def_lang,
        )
        langs = [(def_lang, 0)]
    except Exception as exc:
        logger.error(exc)
        langs = [("en", 0)]

    del conf

    # return first enrty's lang
    if set_languages is None:
        def_lang = langs[0][0]
    else:
        def_lang = "en"

        # pick the first in Detector(text).languages

        # just to silence pyright
        # set_languages_: List[str] = [""] if set_languages is None else set_languages

        for elm in langs:
            if elm[0] in set_languages:  # type: ignore
                def_lang = elm[0]
                break

    # set_languages is set
    if not isinstance(set_languages, (list, tuple)):
        logger.warning("set_languages (%s) ought to be a list/tuple")

    return def_lang
