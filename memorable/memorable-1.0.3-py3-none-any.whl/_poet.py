import secrets
import string

from memorable import _word_bank

_EXTRA_CHARS = string.ascii_lowercase + string.digits

NON_NAMES = list(set(
    _word_bank.NOUNS
    + _word_bank.VERBS
    + _word_bank.ADJECTIVES
    + _word_bank.ADVERBS
))

def name(extra_characters: int = 0) -> str:
    """
    Create a memorable name.

    :param extra_characters:
        The number of extra chracters that should be added to the
        end of the string. This is intended to help reduce collisions if
        the string is being used as an ID.
    """
    name = secrets.choice(_word_bank.NAMES)
    adjective = secrets.choice(_word_bank.ADJECTIVES)
    adverb = secrets.choice(_word_bank.ADVERBS)
    result = f'{name}-the-{adverb}-{adjective}'
    return _pad_with_extra_characters(result, extra_characters)


def action(extra_characters: int = 0) -> str:
    """
    Create a memorable action.

    :param extra_characters:
        The number of extra chracters that should be added to the
        end of the string. This is intended to help reduce collisions if
        the string is being used as an ID.
    """
    verb = secrets.choice(_word_bank.VERBS)
    adjective = secrets.choice(_word_bank.ADJECTIVES)
    noun = secrets.choice(_word_bank.NOUNS)
    article = secrets.choice(['a', 'the'])
    article = 'an' if adjective[0] in 'aeiou' and article == 'a' else article
    result = f'{verb}-{article}-{adjective}-{noun}'
    return _pad_with_extra_characters(result, extra_characters)


def thing(kind: _word_bank.NounTypes = None, extra_characters: int = 0) -> str:
    """
    Create a memorable thing.

    :param kind:
        The kind of thing to create a string for. This can be an animal,
        element, occupation, etc.
    :param extra_characters:
        The number of extra chracters that should be added to the
        end of the string. This is intended to help avoid collisions.
    """
    adjective = secrets.choice(_word_bank.ADJECTIVES)
    adverb = secrets.choice(_word_bank.ADVERBS)
    noun_population = (
        _word_bank.NOUNS if kind is None else _word_bank.NOUN_MAP[kind]
    )
    noun = secrets.choice(noun_population)
    result = f'{adverb}-{adjective}-{noun}'
    return _pad_with_extra_characters(result, extra_characters)


def code_phrase(words: int = 4) -> str:
    """
    Create a random phrase of four words. No effort is taken to make
    it appear as a coherent english phrase.

    :param words:
        The number of words to include in the phrase.
    """
    return '-'.join([secrets.choice(NON_NAMES) for _ in range(words)])


def _pad_with_extra_characters(base: str, count: int) -> str:
    """
    Pad the given base string out with `count` random characters.

    :param base:
        The base string value to append to.
    :param count:
        The number of characters to add.
    :return:
        The base padded with the specified number of extra characters.
    """
    if count == 0:
        return base
    padding = ''.join(secrets.choice(_EXTRA_CHARS) for _ in range(count))
    return f'{base}-{padding}'