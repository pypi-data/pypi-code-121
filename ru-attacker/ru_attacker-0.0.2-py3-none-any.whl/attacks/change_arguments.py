from natasha import (
    Segmenter,
    NewsEmbedding,
    NewsSyntaxParser,
    Doc
)
from .basic_attack import BasicAttack
import pymorphy2

__all__ = ["ChangeArguments"]


class ChangeArguments(BasicAttack):
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()
        self.segmenter = Segmenter()
        self.syntax_parser = NewsSyntaxParser(NewsEmbedding())

    def change_args(self, text):
        def inflect(word, case):
            if not case:
                return word.word
            w = word.inflect({case})
            if w:
                return w.word
            else:
                return word.word

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
            return text
        if len(idx) % 2 == 0:
            for i in range(0, len(idx), 2):
                first = self.morph.parse(args[idx[i]].text)[0]
                second = self.morph.parse(args[idx[i + 1]].text)[0]
                case_first = first.tag.case
                case_second = second.tag.case
                new_first = inflect(first, case_second)
                new_second = inflect(second, case_first)
                args[idx[i]] = new_second
                args[idx[i + 1]] = new_first
        else:
            first = self.morph.parse(args[idx[0]].text)[0]
            second = self.morph.parse(args[idx[1]].text)[0]
            third = self.morph.parse(args[idx[2]].text)[0]
            case_first = first.tag.case
            case_second = second.tag.case
            case_third = third.tag.case
            new_first = inflect(first, case_third)
            new_second = inflect(second, case_first)
            new_third = inflect(third, case_second)
            args[idx[0]] = new_second
            args[idx[1]] = new_third
            args[idx[2]] = new_first
            if len(idx) > 3:
                for i in range(3, len(idx), 2):
                    first = self.morph.parse(args[idx[i]].text)[0]
                    second = self.morph.parse(args[idx[i + 1]].text)[0]
                    case_first = first.tag.case
                    case_second = second.tag.case
                    new_first = inflect(first, case_second)
                    new_second = inflect(second, case_first)
                    args[idx[i]] = new_second
                    args[idx[i + 1]] = new_first
        sentence = [args[token.id] if token.id in idx else token.text for token in doc.tokens]
        return " ".join(sentence)

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
                transformed = self.change_args(hypothesis)
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
                if prediction == 1:
                    results["attack"].append("succeeded")
                    self.print_results(results)
                else:
                    results["attack"].append("failed")
                    self.print_results(results)
        print(
            f"Accuracy before attack {round(correct / total, 2)} --> Accuracy after attack {round(correct_attack / total, 2)}"
        )
        print(f"Success rate {round(results['attack'].count('succeeded') / len(results['attack']), 2)}")
        return results
