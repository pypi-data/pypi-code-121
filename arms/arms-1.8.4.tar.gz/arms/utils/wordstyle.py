from typing import Tuple, List, NamedTuple, Dict
from enum import Enum
from arms.utils.common import captitalize
import re


class WordStyle(Enum):
    upper_camel = 1
    lower_camel = 2
    upper_snake = 3
    lower_snake = 4
    upper_minus = 5
    lower_minus = 6
    other = 7


class WordSeed(NamedTuple):
    word_style: WordStyle
    tokens: List[str]

    def __str__(self) -> str:
        if not self.tokens:
            return ''
        elif self.word_style == WordStyle.upper_camel:
            return ''.join(token.capitalize() for token in self.tokens)
        elif self.word_style == WordStyle.lower_camel:
            return self.tokens[0] + ''.join(token.capitalize() for token in self.tokens[1:])
        elif self.word_style == WordStyle.upper_snake:
            return '_'.join(self.tokens).upper()
        elif self.word_style == WordStyle.lower_snake:
            return '_'.join(self.tokens)
        elif self.word_style == WordStyle.upper_minus:
            return '-'.join(self.tokens).upper()
        elif self.word_style == WordStyle.lower_minus:
            return '-'.join(self.tokens)
        else:
            return ''.join(self.tokens)

    @classmethod
    def of(cls, word: str) -> 'WordSeed':
        if '_' in word:
            if re.match(r'^[a-z0-9_]+$', word):
                return WordSeed(WordStyle.lower_snake, word.split('_'))
            elif re.match(r'^[A-Z0-9_]+$', word):
                return WordSeed(WordStyle.upper_snake, [seg.lower() for seg in word.split('_')])
        elif '-' in word:
            if re.match(r'^[a-z0-9-]+$', word):
                return WordSeed(WordStyle.lower_minus, word.split('-'))
            elif re.match(r'^[A-Z0-9-]+$', word):
                return WordSeed(WordStyle.upper_minus, [seg.lower() for seg in word.split('-')])
        elif re.match(r'^[A-Z][A-Za-z0-9]+$', word):
            return WordSeed(WordStyle.upper_camel, [seg.lower() for seg in re.findall(r'[A-Z][a-z0-9]*', word)])
        elif re.match(r'^[a-z][A-Za-z0-9]+$', word):
            return WordSeed(WordStyle.lower_camel, [seg.lower() for seg in re.findall(r'[A-Z][a-z0-9]*', captitalize(word))])
        return WordSeed(WordStyle.other, [word])


def word_to_style(word: str, style: WordStyle) -> str:
    word_seed = WordSeed.of(word)
    return str(WordSeed(style, word_seed.tokens))


def replace_dict(oldword: str, newword: str):
    old_word_seed = WordSeed.of(oldword)
    new_word_seed = WordSeed.of(newword)
    if len(old_word_seed.tokens) == 1:  # 如果oldword非词组，则newword也按非词组处理
        new_word_seed = WordSeed.of(''.join(new_word_seed.tokens))
    return {
        str(WordSeed(word_style, old_word_seed.tokens)): str(WordSeed(word_style, new_word_seed.tokens))
        for word_style
        in [
            WordStyle.upper_snake, WordStyle.lower_snake,
            WordStyle.upper_minus, WordStyle.lower_minus,
            WordStyle.upper_camel, WordStyle.lower_camel,
        ]
    }


def replace_all(text: str, repl_dict: Dict):
    for in_word, out_word in repl_dict.items():
        text = text.replace(in_word, out_word)
    return text
