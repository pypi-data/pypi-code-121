import hashlib
from functools import reduce

from django.urls import reverse
from django.conf import settings
from django.utils.translation import get_language
from django_jinja import library
from vuejs_translate.views import LanguageTranslation

import jinja2

LANGUAGES_HASHES = {}


@library.global_function
def hashed_translation_url():
    """
    Usage: {{ hashed_translation_url() }}
    """

    active_language = get_language()

    if active_language not in LANGUAGES_HASHES:
        LANGUAGES_HASHES[active_language] = make_language_translation_hash(get_language())

    return reverse(
        "vuejs_translate:js-i18n",
        kwargs={'hash': LANGUAGES_HASHES[active_language]}
    )


def make_language_translation_hash(language: str) -> str:
    translation = LanguageTranslation(language)

    translation_hash = hashlib.md5()

    [make_file_hash(x, translation_hash) for x in translation.get_translation_paths()]

    return translation_hash.hexdigest()[:12]


def make_file_hash(name: str, translation_hash):
    with open(name, 'rb') as content:
        if content is None:
            return None

        while 1:
            chunk = content.read(64 * 2 ** 10)

            if not chunk:
                break

            translation_hash.update(chunk)
