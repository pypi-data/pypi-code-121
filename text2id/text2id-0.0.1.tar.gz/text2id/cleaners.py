""" from https://github.com/keithito/tacotron """
import re
from .u2a import u2a
from .numbers_normalization import normalize_numbers

"""
Cleaners are transformations that run over the input text at both training and
eval time.

Cleaners can be selected by passing a comma-delimited list of cleaner names as
the "cleaners" hyperparameter.
Some cleaners are English-specific. You'll typically want to use:
1. "english_cleaners" for English text
2. "transliteration_cleaners" for non-English text that can be transliterated
to ASCII using the Unidecode library (https://pypi.python.org/pypi/Unidecode)
3. "basic_cleaners" if you do not want to transliterate (in this case, you
should also update the symbols in symbols.py to match your data).
"""


# Regular expression matching whitespace:
_whitespace_re = re.compile(r'\s+')

# List of (regular expression, replacement) pairs for abbreviations:
_abbreviations = [(re.compile('\\b%s\\.' % x[0], re.IGNORECASE), x[1])
                  for x in [
                            ('mrs', 'misess'),
                            ('mr', 'mister'),
                            ('dr', 'doctor'),
                            ('st', 'saint'),
                            ('co', 'company'),
                            ('jr', 'junior'),
                            ('maj', 'major'),
                            ('gen', 'general'),
                            ('drs', 'doctors'),
                            ('rev', 'reverend'),
                            ('lt', 'lieutenant'),
                            ('hon', 'honorable'),
                            ('sgt', 'sergeant'),
                            ('capt', 'captain'),
                            ('esq', 'esquire'),
                            ('ltd', 'limited'),
                            ('col', 'colonel'),
                            ('ft', 'fort'),
]]


class Cleaner:
    def __init__(self, convert_to_ascii=None,
                 cleaner_names=["english_cleaners"]):
        if convert_to_ascii is not None:
            self.convert_to_ascii = convert_to_ascii
        self.cleaner_names = cleaner_names

    @staticmethod
    def expand_abbreviations(text):
        for regex, replacement in _abbreviations:
            text = re.sub(regex, replacement, text)
        return text

    @staticmethod
    def expand_numbers(text):
        return normalize_numbers(text)

    @staticmethod
    def lowercase(text):
        return text.lower()

    @staticmethod
    def collapse_whitespace(text):
        return re.sub(_whitespace_re, ' ', text)

    @staticmethod
    def convert_to_ascii(text):
        return u2a(text)

    def basic_cleaners(self, text):
        """
        Basic pipeline that lowercases and collapses whitespace without
        transliteration.
        """
        text = self.lowercase(text)
        text = self.collapse_whitespace(text)
        return text

    def transliteration_cleaners(self, text):
        """Pipeline for non-English text that transliterates to ASCII."""
        text = self.convert_to_ascii(text)
        text = self.lowercase(text)
        text = self.collapse_whitespace(text)
        return text

    def english_cleaners(self, text):
        """
        Pipeline for English text, including number and abbreviation
        expansion.
        """
        text = self.convert_to_ascii(text)
        text = self.lowercase(text)
        text = self.expand_numbers(text)
        text = self.expand_abbreviations(text)
        text = self.collapse_whitespace(text)
        return text

    def clean(self, text, cleaner_names=None):
        if cleaner_names is None:
            cleaner_names = self.cleaner_names

        for name in cleaner_names:
            cleaner = getattr(self, name)
            if not cleaner:
                raise Exception('Unknown cleaner: %s' % name)
            text = cleaner(text)
        return text
