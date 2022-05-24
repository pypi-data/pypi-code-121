from .basic_attack import BasicAttack
from transformers import pipeline
import torch

__all__ = ["Summarization"]


class Summarization(BasicAttack):
    def __init__(self):
        if torch.cuda.is_available():
            device = 0
        else:
            device = -1
        self.summarizer = pipeline("summarization", model="IlyaGusev/mbart_ru_sum_gazeta",
                              tokenizer="IlyaGusev/mbart_ru_sum_gazeta", device=device)

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
                results["original label"].append(label)
                results["original premise"].append(premise)
                results["original hypothesis"].append(hypothesis)
                correct += 1
                if len(premise) < 200:
                    correct_attack += 1
                    results["attacked label"].append(None)
                    results["transformed"].append(None)
                    results["attack"].append("skipped")
                    self.print_results(results)
                    continue
                transformed = self.summarizer(premise, max_length=50)[0]["summary_text"]
                prediction = model.predict(model.prepare_data(premise, transformed))
                results["attacked label"].append(prediction)
                results["transformed"].append(transformed)
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
