from nlp_tools.tokenizer.base_tokenizer import ABCTokenizer


class ListTokenizer(ABCTokenizer):
    """list tokenizer
    """

    def __init__(self):
        pass

    def tokenize(self, text: str, **kwargs):
        """
        Tokenize text into token sequence
        Args:
            text: target text sample

        Returns:
            List of tokens in this sample
        """

        return list(text)

    def encode(self, text: str, **kwargs):
        """
        Tokenize text into token sequence
        Args:
            text: target text sample

        Returns:
            List of tokens in this sample
        """

        return list(text)

if __name__ == '__main__':
    a = ListTokenizer()
    print(a.to_dict())