from .basic_transformation import BasicTransformation
import pymorphy2
from natasha import (
    Segmenter,
    NewsEmbedding,
    NewsSyntaxParser,
    Doc
)

__all__ = ["ChangeArguments"]


class ChangeArguments(BasicTransformation):
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()
        self.segmenter = Segmenter()
        self.syntax_parser = NewsSyntaxParser(NewsEmbedding())

    def transform(self, text):
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.parse_syntax(self.syntax_parser)
        root = None
        args = {}
        idx = []
        for token in doc.tokens:
            if token.rel in ["root", "csubj"] and not root:
                root = token.id
        if root:
            for token in doc.tokens:
                if token.head_id == root and token.rel in ["nsubj", "obj", "iobj", "obl"]:
                    args[token.id] = token
                    idx.append(token.id)
        if len(idx) < 2:
            return [text]
        if len(idx) % 2 == 0:
            for i in range(0, len(idx), 2):
                first = self.morph.parse(args[idx[i]].text)[0]
                second = self.morph.parse(args[idx[i + 1]].text)[0]
                case_first = first.tag.case
                case_second = second.tag.case
                new_first = self.inflect(first, case_second)
                new_second = self.inflect(second, case_first)
                args[idx[i]] = new_second
                args[idx[i + 1]] = new_first
        else:
            first = self.morph.parse(args[idx[0]].text)[0]
            second = self.morph.parse(args[idx[1]].text)[0]
            third = self.morph.parse(args[idx[2]].text)[0]
            case_first = first.tag.case
            case_second = second.tag.case
            case_third = third.tag.case
            new_first = self.inflect(first, case_third)
            new_second = self.inflect(second, case_first)
            new_third = self.inflect(third, case_second)
            args[idx[0]] = new_second
            args[idx[1]] = new_third
            args[idx[2]] = new_first
            if len(idx) > 3:
                for i in range(3, len(idx), 2):
                    first = self.morph.parse(args[idx[i]].text)[0]
                    second = self.morph.parse(args[idx[i + 1]].text)[0]
                    case_first = first.tag.case
                    case_second = second.tag.case
                    new_first = self.inflect(first, case_second)
                    new_second = self.inflect(second, case_first)
                    args[idx[i]] = new_second
                    args[idx[i + 1]] = new_first
        sentence = [args[token.id] if token.id in idx else token.text for token in doc.tokens]
        return [" ".join(sentence)]

    @staticmethod
    def inflect(word, case):
        if not case:
            return word.word
        w = word.inflect({case})
        if w:
            return w.word
        else:
            return word.word
