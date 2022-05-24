from .basic_attack import BasicAttack
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import torch
from .utils import check_grammar, check_semantics
import random

__all__ = ["BackTranslation"]


class BackTranslation(BasicAttack):
    def __init__(self, languages=None):
        if torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"
        self.model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
        self.tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
        self.tokenizer.src_lang = "ru"
        self.model.to(self.device)
        if languages:
            self.languages = languages
        else:
            self.languages = ["es", "en", "fr", "de", "pt", "bs", "be", "uk", "bg", "hr", "cs", "mk", "pl", "sr", "sk", "sl"]

    def translate_back(self, target_lang, text):
        encoded_ru = self.tokenizer(text, return_tensors="pt")
        generated_tokens = self.model.generate(**encoded_ru.to(self.device),
                                                forced_bos_token_id=self.tokenizer.get_lang_id(target_lang))
        translation = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)

        self.tokenizer.src_lang = target_lang
        encoded_uk = self.tokenizer(translation, return_tensors="pt")
        generated_tokens = self.model.generate(**encoded_uk.to(self.device),
                                                forced_bos_token_id=self.tokenizer.get_lang_id("ru"))
        back_translation = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
        return back_translation[0]

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
                last = None
                success = False
                random.shuffle(self.languages)
                for lang in self.languages:
                    transformed = self.translate_back(lang, hypothesis)
                    if not check_semantics(hypothesis, transformed):
                        continue
                    if not check_grammar(transformed):
                        continue
                    prediction = model.predict(model.prepare_data(premise, transformed))
                    if label != prediction:
                        results["original label"].append(label)
                        results["original premise"].append(premise)
                        results["original hypothesis"].append(hypothesis)
                        results["transformed"].append(transformed)
                        results["attacked label"].append(prediction)
                        results["attack"].append("succeeded")
                        self.print_results(results)
                        success = True
                        break
                    else:
                        last = transformed
                if not success:
                    if last:
                        correct_attack += 1
                        results["original label"].append(label)
                        results["original premise"].append(premise)
                        results["original hypothesis"].append(hypothesis)
                        results["transformed"].append(last)
                        results["attacked label"].append(label)
                        results["attack"].append("failed")
                        self.print_results(results)
                    else:
                        correct_attack += 1
                        results["original label"].append(label)
                        results["original premise"].append(premise)
                        results["original hypothesis"].append(hypothesis)
                        results["transformed"].append(None)
                        results["attack"].append("skipped")
                        results["attacked label"].append(None)
                        self.print_results(results)
        print(
            f"Accuracy before attack {round(correct / total, 2)} --> Accuracy after attack {round(correct_attack / total, 2)}"
        )
        print(f"Success rate {round(results['attack'].count('succeeded')/len(results['attack']), 2)}")
        return results
