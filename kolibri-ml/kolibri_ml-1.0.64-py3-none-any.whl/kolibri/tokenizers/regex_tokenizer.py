import regex as re
import unicodedata
from kolibri.tokenizers.tokenizer import Tokenizer
from kdmt.dict import update

TOKEN_RE = r"""@s \b | (?=[\w\p{So}]) (?!\w'[Hh]) \X+? (?: @s? (?!w) | \b) | \w' """

#TOKEN_RE_WITH_PUNCTUATION = r"""@s \b | [\p{punct}]+ | (?=[\w\p{So}]) (?!\w'[Hh]) \data+? (?: @s? (?!w) | \b) | \w' """


class RegexpTokenizer(Tokenizer):
    """
    A tokenizer that splits a string using a regular expression, which
    matches either the tokens or the separators between tokens.
    """

    defaults = {
        "fixed": {
            'pattern': r"\b(?:[A-Za-z][@\.A-Za-z-][@\.A-Za-z]|['\w\p{So}]{2,}|(?:\d+(?:[\.,:]\d+)*))\b",
            'flags': re.V1 | re.WORD | re.VERBOSE
        },

        "tunable": {
        }
    }

    def __init__(self, parameters=None):

        # If they gave us a regexp object, extract the regexes.
        super().__init__(parameters)

        if 'pattern' in self.hyperparameters['fixed']:
            pattern = self.hyperparameters['fixed']['pattern']
        else:
            pattern=self.defaults['fixed']['pattern']

        if 'flags' in self.hyperparameters['fixed']:
            self._flags = self.hyperparameters['fixed']['flags']
        else:
            self._flags=self.defaults['fixed']['flags']

        if self.get_parameter("include-punctuation"):
            self._regexp = re.compile(pattern+r" | [\p{punct}]+", self._flags)
        else:
            self._regexp = re.compile(pattern, self._flags)

    def __hash__(self):
        return hash(self.name)

    def tokenize(self, text):
        text=super().tokenize(text
                              )
        return self._regexp.findall(str(text))

    def update_default_hyper_parameters(self):
        self.defaults=update(self.defaults, RegexpTokenizer.defaults)
        super().update_default_hyper_parameters()


tokenize=RegexpTokenizer().tokenize

from kolibri.registry import ModulesRegistry
ModulesRegistry.add_module(RegexpTokenizer.name, RegexpTokenizer)



if __name__ == '__main__':
    text = """"Please add the 'Statutory > NL-Sick Leave' => See table below.
    Aujourd'hui qu'il soit ainsi
    but don't
    Company
    UPI
    Legal Name - Last Name
    Preferred Name - First Name
    Type of Leavé
    Start of Leave
    Estimated Last Day of Leave
    Actual Last Day of Leave
    6079 AbbVie BV Commercial
    10373417
    Bosua
    Rosanna
    Statutory > NL-Sick Leave
    29-APR-2019
    28-APR-2020
    6079 AbbVie BV Commercial
    10355526
    Scholtes
    Monique
    Statutory > NL-Sick Leave
    26-NOV-2018
    25-NOV-2019
    Thanks!
    Met vriendelijke groet"""

    tokenizer = RegexpTokenizer({'include-punctuation':False})
    tokens = tokenizer.tokenize(text)
    for t in tokens:
        print(t)
