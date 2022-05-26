from attacks.basic_attack import BasicAttack

__all__ = ["AddProverb"]


class AddProverb(BasicAttack):
    @BasicAttack.attack_decorator
    def attack(self, results, model, premise, hypothesis, label, correct_attack):
        transformed = premise + " Без труда не выловишь и рыбку из пруда."
        prediction, results = self.predict_after_transform_premise(model, premise, transformed, results)
        if label == prediction:
            correct_attack += 1
            return results, "failed", correct_attack
        else:
            return results, "succeeded", correct_attack
