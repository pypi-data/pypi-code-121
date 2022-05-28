from .basic_transformation import BasicTransformation
import nltk
import random

__all__ = ["WordOrder"]


class WordOrder(BasicTransformation):
    def transform(self, text):
        transformed = nltk.word_tokenize(text)
        random.shuffle(transformed)
        transformed = " ".join(transformed)
        return [transformed]