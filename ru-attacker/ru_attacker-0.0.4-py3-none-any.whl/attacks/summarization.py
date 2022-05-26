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

    @BasicAttack.attack_decorator
    def attack(self, results, model, premise, hypothesis, label, correct_attack):
        if len(premise) < 200:
            return results, "skipped", correct_attack
        transformed = self.summarizer(premise, max_length=50)[0]["summary_text"]
        prediction, results = self.predict_after_transform_premise(model, premise, transformed, results)
        if label == prediction:
            correct_attack += 1
            return results, "failed", correct_attack
        else:
            return results, "succeeded", correct_attack
