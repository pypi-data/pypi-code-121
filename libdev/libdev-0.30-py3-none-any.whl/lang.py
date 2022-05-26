"""
Natural language processing functionality
"""

TRANSLITERATION = {
    'а': 'a',
    'б': 'b',
    'в': 'v',
    'г': 'g',
    'д': 'd',
    'е': 'e',
    'ё': 'e',
    'ж': 'zh',
    'з': 'z',
    'и': 'i',
    'й': 'y',
    'к': 'k',
    'л': 'l',
    'м': 'm',
    'н': 'n',
    'о': 'o',
    'п': 'p',
    'р': 'r',
    'с': 's',
    'т': 't',
    'у': 'u',
    'ф': 'f',
    'х': 'kh',
    'ц': 'ts',
    'ч': 'ch',
    'ш': 'sh',
    'щ': 'shch',
    'ъ': '',
    'ы': 'y',
    'ь': '',
    'э': 'e',
    'ю': 'yu',
    'я': 'ya',
}


def get_form(count, variations):
    """ Get form of a noun with a number """

    count = abs(count)

    if count % 10 == 1 and count % 100 != 11:
        return variations[0]

    if count % 10 in (2, 3, 4) and count % 100 not in (12, 13, 14):
        return variations[1]

    return variations[2]

def transliterate(data):
    """ Transliterate RU → EN """

    if data is None:
        return ''

    return ''.join(TRANSLITERATION[i] for i in data.strip().lower())
