from typing import Union, List

_mapping_u2a = {
    # German
    'Ü': 'UE',
    'Ä': 'AE',
    'Ö': 'OE',
    'ü': 'ue',
    'ä': 'ae',
    'ö': 'oe',
    '\u00df': 'ss',
    # French
    'é': 'e',
    'à': 'a',
    'è': 'e',
    'ù': 'u',
    'â': 'a',
    'ê': 'e',
    'î': 'i',
    'ô': 'o',
    'û': 'u',
    'ç': 'c',
    'É': 'E',
    'À': 'A',
    'È': 'E',
    'Ù': 'U',
    'Â': 'A',
    'Ê': 'E',
    'Î': 'I',
    'Ô': 'O',
    'Û': 'U',
    'Ç': 'C',
    # Spanish
    'ñ': 'n',
    'Ñ': 'N',
    # Russian
    'а': 'a',
    'б': 'b',
    'в': 'v',
    'г': 'g',
    'д': 'd',
    'е': 'e',
    'ж': 'zh',
    'з': 'z',
    'и': 'i',
    'й': 'i',
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
    'ы': 'y',
    'э': 'e',
    'ю': 'iu',
    'я': 'ia',
    'А': 'A',
    'Б': 'B',
    'В': 'V',
    'Г': 'G',
    'Д': 'D',
    'Е': 'E',
    'Ж': 'Zh',
    'З': 'Z',
    'И': 'I',
    'Й': 'I',
    'К': 'K',
    'Л': 'L',
    'М': 'M',
    'Н': 'N',
    'О': 'O',
    'П': 'P',
    'Р': 'R',
    'С': 'S',
    'Т': 'T',
    'У': 'U',
    'Ф': 'F',
    'Х': 'Kh',
    'Ц': 'Ts',
    'Ч': 'Ch',
    'Ш': 'Sh',
    'Щ': 'Shch',
    'Ы': 'Y',
    'Э': 'E',
    'Ю': 'Iu',
    'Я': 'Ia',
}

_trans_u2a = str.maketrans(_mapping_u2a)


def u2a(utext: Union[List[str], str]) -> Union[List[str], str]:
    """
    Convert German, French, Spanish, Russian symbols in text to English symbols.
    :param utext: string or list of strings
    :return: string or list of strings
    """
    if type(utext) == str:
        return utext.translate(_trans_u2a)
    else:
        res = [s.translate(_trans_u2a) for s in utext]
        return res


if __name__ == "__main__":
    for k, v in _mapping_u2a.items():
        print(k, v)
    words = ["МИР", "Müller", "célèbre", ""]
    print(u2a(words))
