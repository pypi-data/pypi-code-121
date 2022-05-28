from .basic_transformation import BasicTransformation
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import torch
import random

__all__ = ["BackTranslation"]


class BackTranslation(BasicTransformation):
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

    def transform(self, text):
        transformed = []
        for lang in self.languages:
            transformed.append(self.translate_back(lang, text))
        random.shuffle(transformed)
        return transformed

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