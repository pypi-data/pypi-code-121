from attacks.basic_attack import BasicAttack
import nltk
import random

__all__ = ["WordOrder"]


class WordOrder(BasicAttack):
    @BasicAttack.attack_decorator
    def attack(self, results, model, premise, hypothesis, label, correct_attack):
        transformed = nltk.word_tokenize(hypothesis)
        random.shuffle(transformed)
        transformed = " ".join(transformed)
        prediction, results = self.predict_after_transform_hypothesis(model, premise, transformed, results)
        if label == prediction:
            correct_attack += 1
        if prediction == 1:
            return results, "succeeded", correct_attack
        else:
            return results, "failed", correct_attack
