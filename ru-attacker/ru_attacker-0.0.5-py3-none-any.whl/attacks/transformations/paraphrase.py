from .basic_transformation import BasicTransformation
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

__all__ = ["Paraphrase"]


class Paraphrase(BasicTransformation):
    def __init__(self):
        if torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"
        MODEL_NAME = 'cointegrated/rut5-base-paraphraser'
        self.model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
        self.tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
        self.model.to(self.device).eval()

    def transform(self, text):
        x = self.tokenizer(text, return_tensors='pt', padding=True).to(self.device)
        max_size = int(x.input_ids.shape[1] * 1.5 + 10)
        out = self.model.generate(**x, encoder_no_repeat_ngram_size=4, num_beams=5, max_length=max_size,
                                        do_sample=False)
        return [self.tokenizer.decode(out[0], skip_special_tokens=True)]
