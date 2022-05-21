from decimal import Decimal
from fractions import Fraction
from typing import Type

from numeric_methods.language import LANGUAGE, TRANSLATE
from numeric_methods.language.docs.settings import (
    GET_LANGUAGE_DOCS, SET_LANGUAGE_DOCS,
    DEFAULT_EPSILON_DOCS, GET_EPSILON_DOCS, RESTORE_EPSILON_DOCS, SET_EPSILON_DOCS
)
from numeric_methods.mathematics import EPSILON

NUMBER = Decimal | float | Fraction


@TRANSLATE.documentation(GET_LANGUAGE_DOCS)
def get_language() -> str:
    return LANGUAGE.current


@TRANSLATE.documentation(SET_LANGUAGE_DOCS)
def set_language(name: str) -> bool:
    language = LANGUAGE.get_acceptable(name)
    if language is not None:
        LANGUAGE.current = language
        TRANSLATE.update()
        return True
    return False


@TRANSLATE.documentation(DEFAULT_EPSILON_DOCS)
def default_epsilon() -> str:
    return EPSILON.get_default()


@TRANSLATE.documentation(GET_EPSILON_DOCS)
def get_epsilon(kind: Type[NUMBER] = float) -> NUMBER:
    return EPSILON.with_context(kind(0) if callable(kind) else kind)


@TRANSLATE.documentation(RESTORE_EPSILON_DOCS)
def restore_epsilon():
    EPSILON.restore()


@TRANSLATE.documentation(SET_EPSILON_DOCS)
def set_epsilon(value: str) -> bool:
    return EPSILON.set(value)
