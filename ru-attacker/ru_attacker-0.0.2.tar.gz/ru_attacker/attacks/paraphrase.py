from .basic_attack import BasicAttack
import torch
from .utils import check_grammar, check_semantics
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

    def paraphrase(self, text, beams=5, grams=4, do_sample=False):
        x = self.tokenizer(text, return_tensors='pt', padding=True).to(self.device)
        max_size = int(x.input_ids.shape[1] * 1.5 + 10)
        out = self.model.generate(**x, encoder_no_repeat_ngram_size=grams, num_beams=beams, max_length=max_size,
                                        do_sample=do_sample)
        return self.tokenizer.decode(out[0], skip_special_tokens=True)

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
                transformed = self.paraphrase(hypothesis)
                results["original label"].append(label)
                results["original premise"].append(premise)
                results["original hypothesis"].append(hypothesis)
                results["transformed"].append(transformed)
                if not check_semantics(hypothesis, transformed):
                    correct_attack += 1
                    results["attack"].append("skipped")
                    results["attacked label"].append(None)
                    self.print_results(results)
                    continue
                if not check_grammar(transformed):
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
