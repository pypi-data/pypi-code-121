from .basic_attack import BasicAttack
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

__all__ = ["Paraphrase"]


class Paraphrase(BasicAttack):
    def __init__(self):
        if torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"
        MODEL_NAME = 'cointegrated/rut5-base-paraphraser'
        self.model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
        self.tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
        self.model.to(self.device).eval()

    @BasicAttack.attack_decorator
    def attack(self, results, model, premise, hypothesis, label, correct_attack):
        transformed = self.paraphrase(hypothesis)
        if not self.check_semantics(hypothesis, transformed) or not self.check_grammar(transformed):
            return results, "skipped", correct_attack
        prediction, results = self.predict_after_transform_hypothesis(model, premise, transformed, results)
        if label == prediction:
            correct_attack += 1
            return results, "failed", correct_attack
        else:
            return results, "succeeded", correct_attack

    def paraphrase(self, text, beams=5, grams=4, do_sample=False):
        x = self.tokenizer(text, return_tensors='pt', padding=True).to(self.device)
        max_size = int(x.input_ids.shape[1] * 1.5 + 10)
        out = self.model.generate(**x, encoder_no_repeat_ngram_size=grams, num_beams=beams, max_length=max_size,
                                        do_sample=do_sample)
        return self.tokenizer.decode(out[0], skip_special_tokens=True)