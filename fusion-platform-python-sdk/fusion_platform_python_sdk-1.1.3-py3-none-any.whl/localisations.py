"""
Translations generator file.

author: Matthew Casey

&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)
"""

import os
from pathlib import Path
import yaml


def get_all_values(nested_dictionary, values=None, hierarchy=None, prefix=None, strip=None):
    """
    Recursively builds a dictionary of all the leaves in a nested dictionary.

    Args:
        nested_dictionary: The nested dictionary to traverse.
        values: The current set of extracted leaf values.
        hierarchy: The hierarchy for the keys.
        prefix: Any prefix to add to the keys.
        strip: Any value which should be stripped from the hierarchy.

    Returns:
        The dictionary of leaf values.
    """
    values = {} if values is None else values
    hierarchy = [] if hierarchy is None else hierarchy
    prefix = [] if prefix is None else prefix

    for key, value in nested_dictionary.items():
        path = hierarchy + [key]

        try:
            path.remove(strip)
        except:
            pass

        if type(value) is dict:
            values = {**get_all_values(value, hierarchy=path, prefix=prefix, strip=strip), **values}
        else:
            values = {'.'.join(prefix + path): value, **values}

    return values


# Find all the translation files, parse them and then build a complete list of the translations.
translations_by_locale = {}

for path in Path('resources/locales').rglob('*.yml'):
    print(f"Extracting {path}")
    locale = path.suffixes[0].replace('.', '')
    prefix = list(path.parts[2:-1])  # Strip off the 'resources/locales'.
    prefix += [os.path.splitext(path.stem)[0]]

    translations_by_locale[locale] = {} if translations_by_locale.get(locale) is None else translations_by_locale[locale]

    with open(path, 'r') as file:
        translations_by_locale[locale] = {**translations_by_locale[locale], **get_all_values(yaml.safe_load(file), prefix=prefix, strip=locale)}

# Now output all the translations as a Python file.
with open('fusion_platform/translations.py', 'w') as file:
    file.write('"""\n')
    file.write('Compiled translations.\n')
    file.write('\n')
    file.write('author: Matthew Casey\n')
    file.write('\n')
    file.write('&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)\n')
    file.write('"""\n')
    file.write('\n')
    file.write('# Do not modify this file manually as it is built automatically by the localisations.py script.\n')
    file.write('\n')
    file.write('import i18n\n')
    file.write('\n')
    file.write('# @formatter:off\n')

    for locale, translations in translations_by_locale.items():
        for key, value in translations.items():
            translation = value.replace("'", "\\'")
            file.write(f"i18n.add_translation('{key}', '{translation}', '{locale}')\n")

    file.write('# @formatter:on\n')
