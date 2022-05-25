from nlp_tools.tokenizer.base_tokenizer import ABCTokenizer


class JiebaTokenizer(ABCTokenizer):
    """Jieba tokenizer
    """

    def __init__(self):
        try:
            import jieba
            self._jieba = jieba
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Jieba module not found, please install use `pip install jieba`")

    def tokenize(self, text: str, **kwargs):
        """
        Tokenize text into token sequence
        Args:
            text: target text sample

        Returns:
            List of tokens in this sample
        """

        return list(self._jieba.cut(text, **kwargs))

    def encode(self, text: str, **kwargs):
        """
        Tokenize text into token sequence
        Args:
            text: target text sample

        Returns:
            List of tokens in this sample
        """

        return list(self._jieba.cut(text, **kwargs))
