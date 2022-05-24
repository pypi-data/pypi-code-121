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

    def attack(self, model, dataset):
        results = {
            "original label": [],
            "attacked label": [],
            "original premise": [],
            "original hypothesis": [],
            "transformed": [],
            "attack": []
        }
        total = 0
        correct = 0
        correct_attack = 0
        for i, row in dataset.iterrows():
            total += 1
            premise = row["premise"]
            hypothesis = row["hypothesis"]
            label = row["label"]
            prediction = model.predict(model.prepare_data(premise, hypothesis))
            if label == prediction:
                correct += 1
                transformed = self.yoda_style(hypothesis)
                results["original label"].append(label)
                results["original premise"].append(premise)
                results["original hypothesis"].append(hypothesis)
                results["transformed"].append(transformed)
                if hypothesis == transformed:
                    correct_attack += 1
                    results["attack"].append("skipped")
                    results["attacked label"].append(None)
                    self.print_results(results)
                    continue
                prediction = model.predict(model.prepare_data(premise, transformed))
                results["attacked label"].append(prediction)
                if label == prediction:
                    correct_attack += 1
                    results["attack"].append("failed")
                    self.print_results(results)
                else:
                    results["attack"].append("succeeded")
                    self.print_results(results)
        print(
            f"Accuracy before attack {round(correct / total, 2)} --> Accuracy after attack {round(correct_attack / total, 2)}"
        )
        print(f"Success rate {round(results['attack'].count('succeeded') / len(results['attack']), 2)}")
        return results

