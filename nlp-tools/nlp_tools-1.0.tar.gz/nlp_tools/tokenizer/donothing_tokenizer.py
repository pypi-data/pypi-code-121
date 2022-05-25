from nlp_tools.tokenizer.base_tokenizer import ABCTokenizer


class DoNothingTokenizer(ABCTokenizer):
    """list tokenizer
    """

    def __init__(self):
        pass

    def tokenize(self, text: str, **kwargs):
        return text

    def encode(self, text: str, **kwargs):
        return text

