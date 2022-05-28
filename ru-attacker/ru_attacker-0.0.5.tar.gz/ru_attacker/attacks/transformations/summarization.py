from .basic_transformation import BasicTransformation
from transformers import pipeline
import torch

__all__ = ["Summarization"]


class Summarization(BasicTransformation):
    def __init__(self):
        if torch.cuda.is_available():
            device = 0
        else:
            device = -1
        self.summarizer = pipeline("summarization", model="IlyaGusev/mbart_ru_sum_gazeta",
                              tokenizer="IlyaGusev/mbart_ru_sum_gazeta", device=device)

    def transform(self, text):
        return [self.summarizer(text, max_length=50)[0]["summary_text"]]
