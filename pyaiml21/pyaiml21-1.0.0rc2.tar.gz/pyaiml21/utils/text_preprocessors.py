"""Utilities to preprocess user's input."""
from abc import ABC, abstractmethod
import unicodedata
from typing import List


##############################################################################
#    CJK = Chinese-Japanese-Korean alphabet
##############################################################################
# original post: https://stackoverflow.com/a/30070664/19021375

ranges = [
    # compatibility ideographs
    (ord(u"\u3300"), ord(u"\u33ff")),
    (ord(u"\ufe30"), ord(u"\ufe4f")),
    (ord(u"\uf900"), ord(u"\ufaff")),
    (ord(u"\U0002F800"), ord(u"\U0002fa1f")),

    # Japanese Hiragana
    (ord(u'\u3040'), ord(u'\u309f')),
    # Japanese Katakana
    (ord(u"\u30a0"), ord(u"\u30ff")),
    # cjk radicals supplement
    (ord(u"\u2e80"), ord(u"\u2eff")),
    (ord(u"\u4e00"), ord(u"\u9fff")),
    (ord(u"\u3400"), ord(u"\u4dbf")),
    (ord(u"\U00020000"), ord(u"\U0002a6df")),
    (ord(u"\U0002a700"), ord(u"\U0002b73f")),
    (ord(u"\U0002b740"), ord(u"\U0002b81f")),
    # included as of Unicode 8.0
    (ord(u"\U0002b820"), ord(u"\U0002ceaf"))
]


def is_cjk(char: str) -> bool:
    """Return True if given character is CJK character."""
    return any([from_ <= ord(char) <= to_ for from_, to_ in ranges])


##############################################################################
#                   W o r d   N o r m a l i s a t i o n
##############################################################################

class _Normalizer(ABC):
    @staticmethod
    @abstractmethod
    def normalize(sentence: str) -> str:
        """
        Normalize given sentence to canonical form.

        The canonical form of the sentence in the AIML is defined
        as a sentence with characters capitalized and the interaction
        omitted.

        :param sentence: a sentence to be normalized
        :return: canonical form of the sentence, one that can be used with
            a GraphMaster
        """
        pass


class _SimpleNormalizer(_Normalizer):
    UNICODE_FORM = "NFC"

    @staticmethod
    def normalize(sentence: str) -> str:
        """
        Normalize sentence by converting to uppercase and ignoring punctuation.

        Convert text to uppercase, perform unicode normalisation and keep
        only alphanumeric characters and spaces.

        :param sentence: sentence to be normalized
        :return: canonical form of the sentence

        >>> normalizer = _SimpleNormalizer()
        >>> normalizer.normalize("Simple sentence.") == "SIMPLE SENTENCE"
        True

        >>> text = "This? is, ..., a sentence with punctuation."
        >>> res = "THIS IS  A SENTENCE WITH PUNCTUATION"
        >>> normalizer.normalize(text) == res
        True

        """
        normalized: str = unicodedata.normalize("NFC", sentence)
        uppercase = normalized.upper()
        return "".join(c for c in uppercase if c.isspace() or c.isalnum())


##############################################################################
#             S e n t e n c e   S p l i t t i n g
##############################################################################


class _SentenceSplitter(ABC):
    @staticmethod
    @abstractmethod
    def split(text: str) -> List[str]:
        """
        Split user input into a list of sentences.

        :param text: text to be split
        :return: list of sentences from the text
        """
        pass


class _SimpleSentenceSplitter(_SentenceSplitter):
    @staticmethod
    def split(text: str) -> List[str]:
        """
        Split text on usual sentence boundaries.

        Given ``text``, finds all occurrences of '?', '!', '.', and splits
        it on these positions. Keeps the last characters of the sentence,
        i.e. the sentence boundary is returned with the sentence it belongs to.
        Additionaly, keeps all whitespace characters, so the concatenation
        of the result is exactly the input ``text``.

        :param text:  text to be split
        :return: list of sentences from the text

        >>> splitter = _SimpleSentenceSplitter()
        >>> exp = ["Hello.", " This is a sentence?", " Definitely!"]
        >>> splitter.split("Hello. This is a sentence? Definitely!") == exp
        True


        >>> expected = ["Anyone?!", "    Yes!!!", " I will do it."]
        >>> splitter.split("Anyone?!    Yes!!! I will do it.") == expected
        True

        >>> expected = [".", "a.", "b.", "c.", "d"]
        >>> splitter.split(".a.b.c.d") == expected
        True

        """
        delimiters = u"?!.。？"
        sentences = []
        sentence_start = 0

        for sentence_end, symbol in enumerate(text):
            if symbol in delimiters:
                next_symbol = None \
                    if sentence_end == len(text) - 1 \
                    else text[sentence_end + 1]
                if next_symbol is None or next_symbol not in delimiters:
                    last_sentence = text[sentence_start:sentence_end + 1]
                    sentences.append(last_sentence)
                    sentence_start = sentence_end + 1

        if sentence_start < len(text):
            text_last_sentence = text[sentence_start:]
            sentences.append(text_last_sentence)

        return sentences


##############################################################################
#             W o r d   S p l i t t i n g
##############################################################################


class _WordSplitter(ABC):
    @staticmethod
    @abstractmethod
    def split(sentence: str) -> List[str]:
        """
        Split the `sentence` to a list of words.

        :param sentence: string to be split
        :return: list of words of the sentence
        """
        pass


class _SimpleWordSplitter(_WordSplitter):
    @staticmethod
    def split(sentence: str) -> List[str]:
        """
        Split sentence into words, ignoring any whitespace characters.

        More precisely, return all non-empty subsequences from the sentence,
        that do not contain whitespace characters

        :param sentence: string gto be split
        :return: list of words

        >>> splitter = _SimpleWordSplitter()
        >>> expected = ["This", "is", "a", "sentence."]
        >>> splitter.split("This is a sentence.") == expected
        True

        >>> got = splitter.split("And it has long       spaces")
        >>> expected = ["And", "it", "has", "long", "spaces"]
        >>> got == expected
        True

        >>> splitter.split("             ")
        []

        """
        return sentence.split()


class _CJKSplitter(_WordSplitter):
    @staticmethod
    def split(sentence: str) -> List[str]:
        """
        Split the sentence into a list of characters.

        Treating each character as a word, return a list of non-space
        characters from the sentence.

        :param sentence: text to be split
        :return: list of characters from the sentence, in the same order

        >>> splitter = _CJKSplitter()
        >>> e = ["S", "o", "m", "e",
        ...      "s", "e", "n", "t", "e", "n", "c", "e",
        ...      "."]
        >>> splitter.split("Some sentence.") == e
        True

        >>> expected = ["こ", "れ", "は", "文", "で", "す"]
        >>> splitter.split("これは文です") == expected
        True

        >>> splitter.split("   ")
        []

        """
        return [char for char in sentence if not char.isspace()]


# the functions
def split_sentences(s: str) -> List[str]:
    """Split text `s` to its sentences."""
    return _SimpleSentenceSplitter.split(s)


def normalize_user_input(s: str) -> List[List[str]]:
    """
    Perform latin-alphabet normalisation, split to sentences and each to words.

    Word normalisation consists of UNICODE normalisation and converting
    to uppercase.

    :param s: user input to normalize
    :return: list of sentences, each sentence is a list of words

    Example:
        >>> text = "Hello. How ARE you...."
        >>> expected = [["HELLO"], ["HOW", "ARE", "YOU"]]
        >>> normalize_user_input(text) == expected
        True
    """
    sentences = split_sentences(s)
    normed = map(_SimpleNormalizer.normalize, sentences)
    word_split = map(_SimpleWordSplitter.split, normed)
    return list(word_split)


def normalize_cjk_user_input(s: str) -> List[List[str]]:
    """
    Perform CJK normalisation, split to sentences and each to words.

    CJK (Chinese, Japanses, Korean) normalisation is equivalent
    to using <explode> on each word. Also UNICODE normalisation
    with uppercase-ing is done.

    :param s: user input to normalize
    :return: list of sentences, each sentence is a list of words

    Example:
        >>> text = u"こんにちは。この企画を気に入っていただけたでしょうか？"
        >>> expected = [list("こんにちは"),
        ...             list("この企画を気に入っていただけたでしょうか")]
        >>> normalize_cjk_user_input(text) == expected
        True
    """
    sentences = split_sentences(s)
    normed = map(_SimpleNormalizer.normalize, sentences)
    word_split = map(_CJKSplitter.split, normed)
    return list(word_split)
