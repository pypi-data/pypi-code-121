from .basic_transformation import BasicTransformation

__all__ = ["AddProverb"]


class AddProverb(BasicTransformation):
    def transform(self, text):
        return [text + " Без труда не выловишь и рыбку из пруда."]
