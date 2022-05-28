from natasha import (
    Segmenter,
    NewsEmbedding,
    NewsSyntaxParser,
    Doc
)
from .basic_attack import BasicAttack

__all__ = ["YodaStyle"]


class YodaStyle(BasicAttack):
    def __init__(self):
        self.segmenter = Segmenter()
        self.syntax_parser = NewsSyntaxParser(NewsEmbedding())

    @BasicAttack.attack_decorator
    def attack(self, results, model, premise, hypothesis, label, correct_attack):
        transformed = self.yoda_style(hypothesis)
        if hypothesis == transformed:
            return results, "skipped", correct_attack
        prediction, results = self.predict_after_transform_hypothesis(model, premise, transformed, results)
        if label == prediction:
            correct_attack += 1
            return results, "failed", correct_attack
        else:
            return results, "succeeded", correct_attack

    def yoda_style(self, text):
        def find_children(parent_id, children, tokens):
            # token = tokens[int(parent_id[-1]) - 1]
            for tok in tokens:
                if tok.head_id == parent_id:
                    children = find_children(tok.id, children, tokens)
                    if children == None:
                        return
                    children.append(tok.id)
            return children

        def get_args(arg, tokens):
            args = find_children(arg, [arg], tokens)
            children = []
            for token in tokens:
                if token.id in args:
                    children.append(token.text)
            return " ".join(children), args

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
                        subj, args = get_args(token.id, tokens)
                        idx.extend(args)
                    elif token.rel == "obj":
                        obj, args = get_args(token.id, tokens)
                        idx.extend(args)
        if subj and obj:
            sent = [obj.capitalize(), subj.lower()]
            sent.extend([t.text for t in tokens if t.id not in idx])
            return " ".join(sent)
        else:
            return text
