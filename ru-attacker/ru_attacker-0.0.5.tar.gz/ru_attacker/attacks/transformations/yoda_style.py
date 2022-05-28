from .basic_transformation import BasicTransformation
from natasha import (
    Segmenter,
    NewsEmbedding,
    NewsSyntaxParser,
    Doc
)

__all__ = ["YodaStyle"]


class YodaStyle(BasicTransformation):
    def __init__(self):
        self.segmenter = Segmenter()
        self.syntax_parser = NewsSyntaxParser(NewsEmbedding())

    def transform(self, text):
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.parse_syntax(self.syntax_parser)
        root = None
        idx = []
        tokens = doc.tokens
        subj = None
        obj = None
        for token in tokens:
            if token.rel in ["root", "csubj"] and not root:
                root = token.id
        if root:
            for token in tokens:
                if token.head_id == root:
                    if token.rel == "nsubj":
                        subj, args = self.get_args(token.id, tokens)
                        idx.extend(args)
                    elif token.rel == "obj":
                        obj, args = self.get_args(token.id, tokens)
                        idx.extend(args)
        if subj and obj:
            sent = [obj.capitalize(), subj.lower()]
            sent.extend([t.text for t in tokens if t.id not in idx])
            return [" ".join(sent)]
        else:
            return [text]

    def find_children(self, parent_id, children, tokens):
        for tok in tokens:
            if tok.head_id == parent_id:
                children = self.find_children(tok.id, children, tokens)
                if children == None:
                    return
                children.append(tok.id)
        return children

    def get_args(self, arg, tokens):
        args = self.find_children(arg, [arg], tokens)
        children = []
        for token in tokens:
            if token.id in args:
                children.append(token.text)
        return " ".join(children), args
