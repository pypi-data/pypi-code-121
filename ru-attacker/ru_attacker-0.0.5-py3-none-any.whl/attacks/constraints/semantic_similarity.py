from .basic_constraint import BasicConstraint
import tensorflow_hub as hub
import numpy as np
import tensorflow_text

__all__ = ["SemanticSimilarity"]


class SemanticSimilarity(BasicConstraint):
    def __init__(self):
        self.embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")

    def check(self, original, transformed):
        score = np.inner(self.embed(original), self.embed(transformed))
        if score >= 0.8:
            return True
        else:
            return False
