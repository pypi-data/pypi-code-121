
from modeltranslation.utils import get_translation_fields


def trans_fields(name):
    return tuple(get_translation_fields(name))
