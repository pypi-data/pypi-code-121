""" from https://github.com/keithito/tacotron """
import re

from .cleaners import Cleaner
from .cmudict import CMUDict
from .symbols import symbols
from .used_types import *

# Mappings from symbol to numeric ID and vice versa:
_symbol_to_id = {s: i for i, s in enumerate(symbols)}
_id_to_symbol = {i: s for i, s in enumerate(symbols)}

# Regular expression matching text enclosed in curly braces:
_curly_re = re.compile(r'(.*?)\{(.+?)\}(.*)')


class Text2Id:
    def __init__(self, cmu_dict_path: str = None,
                 convert_to_ascii: Callable = None):
        """
        Class for preprocessing text before feeding to text to speech neural
        network.
        :param cmu_dict_path: path to CMU Pronouncing Dictionary, if None load
        default.
        :param convert_to_ascii: function or callable object for converting
        unicode text ot ascii.
        """
        self.cmudict = CMUDict(cmu_dict_path)
        self.cleaner = Cleaner(convert_to_ascii)

    def get_arpabet(self, word: str):
        word_arpabet = self.cmudict.lookup(word)
        if word_arpabet is not None:
            return "{" + word_arpabet[0] + "}"
        else:
            return word

    def text_to_sequence(self, text: str, cleaner_names: list = None,
                         use_dict: bool = True) -> list:
        """
        Converts a string of text to a sequence of IDs corresponding to the
        symbols in the text.

          The text can optionally have ARPAbet sequences enclosed in curly
          braces embedded in it. For example,
          "Turn left on {HH AW1 S S T AH0 N} Street."

          Args:
            text: string to convert to a sequence
            cleaner_names: names of the cleaner functions to run the text
            throught
            use_dict: if true then converts symbols to arpabet
            (https://en.wikipedia.org/wiki/ARPABET)

          Returns:
            List of integers corresponding to the symbols in the text
        """
        sequence = []

        space = self._symbols_to_sequence(' ')
        # Check for curly braces and treat their contents as ARPAbet:
        while len(text):
            m = _curly_re.match(text)
            if not m:
                clean_text = self.cleaner.clean(text, cleaner_names)
                if use_dict:
                    clean_text = [self.get_arpabet(w)
                                  for w in clean_text.split(" ")]
                    for i in range(len(clean_text)):
                        t = clean_text[i]
                        if t.startswith("{"):
                            sequence += self._arpabet_to_sequence(t[1:-1])
                        else:
                            sequence += self._symbols_to_sequence(t)
                        sequence += space
                else:
                    sequence += self._symbols_to_sequence(clean_text)
                break
            sequence += self._symbols_to_sequence(
                self.cleaner.clean(m.group(1), cleaner_names))
            sequence += self._arpabet_to_sequence(m.group(2))
            text = m.group(3)

        # remove trailing space
        if use_dict:
            sequence = sequence[:-1] if sequence[-1] == space[0] else sequence
        return sequence

    @staticmethod
    def sequence_to_text(sequence: str) -> str:
        """
        Converts a sequence of IDs back to a string
        """
        result = ''
        for symbol_id in sequence:
            if symbol_id in _id_to_symbol:
                s = _id_to_symbol[symbol_id]
                # Enclose ARPAbet back in curly braces:
                if len(s) > 1 and s[0] == '@':
                    s = '{%s}' % s[1:]
                result += s
        return result.replace('}{', ' ')

    def _symbols_to_sequence(self, symbols: list) -> list:
        return [_symbol_to_id[s] for s in symbols
                if self._should_keep_symbol(s)]

    def _arpabet_to_sequence(self, text: str) -> list:
        return self._symbols_to_sequence(['@' + s for s in text.split()])

    @staticmethod
    def _should_keep_symbol(s: str) -> bool:
        return s in _symbol_to_id and s != '_' and s != '~'

    @staticmethod
    def get_symbols() -> list:
        return symbols[:]


if __name__ == "__main__":
    t2i = Text2Id()
    text = "Müller said 11 12 13"
    print(t2i.text_to_sequence(text))
    print(t2i.sequence_to_text(t2i.text_to_sequence(text)))
    print(t2i.text_to_sequence(text, use_dict=False))
    print(t2i.sequence_to_text(t2i.text_to_sequence(text, use_dict=False)))
