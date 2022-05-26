"""i18n bases."""

from typing import Literal

from babel.support import Translations

from .fn import locales, new_log

Lang = Literal[locales]  # noqa

static_translates = dict().fromkeys(locales, {})

for locale in locales:
    static_translates[locale] = Translations.load('i18n', [locale])

log = new_log(__name__)
