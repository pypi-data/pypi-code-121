from random import choice, sample

from .utilities import get_data


PARTS_OF_SPEECH = ['adj', 'adv', 'conj', 'interj',
                   'noun', 'prep', 'pron', 'verb']


def word(count: int | None = None,
         include_pos: list[str] | None = None,
         exclude_pos: list[str] | None = None,
         word_len: int | None = None,
         min_word_len: int = 1,
         max_word_len: int | None = None,
         starts_with: str | None = None,
         ends_with: str | None = None,
         pattern: str | None = None) -> str | list[str]:
    '''
    Returns a random English word or a list of words

    Abbreviation "pos" means "part of speech"

    Args:
        count (int, optional): The number of words to
            be generated. Defaults to None.
        include_pos (list of str, optional): List of parts of speech that will
            be included in the generation. Defaults to `None`
        exclude_pos (list of str, optional): List of parts of speech that will
            be excluded in the generation. Defaults to `None`
        word_len (int, optional): Specifies the length of a word. Ignores the
            `min_word_len` and `max_word_len` parameters. Defaults to `None`
        min_word_len (int, optional): The minimum word length. Defaults to `1`
        max_word_len (int, optional): The maximum word length. Defaults
            to `None`
        starts_with (str, optional): The pattern with which
            the word begins. Defaults to `None`
        ends_with (str, optional): The pattern with which
            the word ends. Defaults to `None`
        pattern (str, optional): The pattern that should be
            contained in the word. Defaults to `None`

    Returns:
        str | list[str]: A random English word if `count` is `None` or
            a list of them if `count` is not `None`

    Raises:
        IndexError: If the word was not found or if the
            desired number of words was not found
    '''
    if not include_pos:
        include_pos = PARTS_OF_SPEECH

    if exclude_pos:
        parts_of_speech = list(set(include_pos) - set(exclude_pos))
    else:
        parts_of_speech = include_pos

    words = []
    for part_of_speech in parts_of_speech:
        pos_words = get_data('parts_of_speech', part_of_speech)
        words.extend(pos_words)

    if max_word_len:
        filtered_words = list(filter(lambda word:
            min_word_len <= len(word) <= max_word_len, words))
    else:
        filtered_words = list(filter(lambda word:
            min_word_len <= len(word), words))

    if word_len:
        filtered_words = list(filter(lambda word:
            word_len == len(word), words))

    if starts_with:
        filtered_words = list(filter(lambda word:
            word.startswith(starts_with), filtered_words))
    if ends_with:
        filtered_words = list(filter(lambda word:
            word.endswith(ends_with), filtered_words))
    if pattern:
        filtered_words = list(filter(lambda word:
            pattern in word, filtered_words))

    if count:
        INDEX_ERROR_DESCRIPTION = 'The desired number of words was not found'

        if not filtered_words:
            raise IndexError(INDEX_ERROR_DESCRIPTION)

        try:
            final_words = sample(filtered_words, count)
        except ValueError:
            raise IndexError(INDEX_ERROR_DESCRIPTION)

        return final_words
    else:
        if not filtered_words:
            raise IndexError('The word was not found')

        return choice(filtered_words)


if __name__ == '__main__':
    print(word())
