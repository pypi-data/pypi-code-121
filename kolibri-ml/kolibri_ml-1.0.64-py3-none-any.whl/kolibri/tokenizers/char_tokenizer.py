import warnings

from kolibri.tokenizers.tokenizer import *


from kdmt.text import remove_punctuations, ngram



def text_to_word_sequence(text,
                          filters=None,
                          lower=True, split=" "):
    """Converts a text to a sequence of words (or tokens).
    # Arguments
        text: Input text (string).
        filters: list (or concatenation) of characters to filter out, such as
            punctuation. Default: ``!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\\t\\n``,
            includes basic punctuation, tabs, and newlines.
        lower: boolean. Whether to convert the input to lowercase.
        split: str. Separator for word splitting.
    # Returns
        A list of words (or tokens).
    """
    if lower:
        text = text.lower()

    if filters:
        text = remove_punctuations(text, split, filters)
    seq = text.split(split)
    return [i for i in seq if i]


class CharTokenizer(Tokenizer):
    """Text tokenization utility class inspired from keras
    """

    defaults = {
        "fixed": {
            "remove-punct": False,
        },
        "tunable": {
            "ngram": {
                "value": 1,
                "type": "integer",
                "range": [1, 5]
            }
        }

    }

    def __init__(self, parameters, **kwargs):

        super().__init__(parameters)

        if 'nb_words' in kwargs:
            warnings.warn('The `nb_words` argument in `Tokenizer` '
                          'has been renamed `num_words`.')
            num_words = kwargs.pop('nb_words')
        if kwargs:
            raise TypeError('Unrecognized keyword arguments: ' + str(kwargs))
        self.lower = self.hyperparameters["fixed"]['do-lower-case']
        self.remove_stopwords = self.hyperparameters["fixed"]["filter-stopwords"]
        self.remove_punctuations = self.hyperparameters["fixed"]["remove-punct"]
        self.punctuations = None

        if self.remove_stopwords:
            self.stopwords = get_stop_words(self.get_parameter('language'))
        self.ngram = self.get_parameter('ngram')


    def update_default_hyper_parameters(self):
        self.defaults=update(self.defaults, CharTokenizer.defaults)
        super().update_default_hyper_parameters()

    def fit(self, training_data, target):
        return self

    def transform(self, texts, **kwargs):
        return self.texts_to_sequences(texts)

    def tokenize(self, text):
        return self.texts_to_sequences([text])

    def get_info(self):
        return "char_tokenizer"

    def texts_to_sequences(self, texts):
        """Transforms each text in texts to a sequence of integers.
        Only top `num_words-1` most frequent words will be taken into account.
        Only words known by the tokenizer will be taken into account.
        # Arguments
            texts: A list of texts (strings).
        # Returns
            A list of sequences.
        """

        return list(self.texts_to_sequences_generator(texts))

    def texts_to_sequences_generator(self, texts):
        """Transforms each text in `texts` to a sequence of integers.
        Each item in texts can also be a list,
        in which case we assume each item of that list to be a token.
        Only top `num_words-1` most frequent words will be taken into account.
        Only words known by the tokenizer will be taken into account.
        # Arguments
            texts: A list of texts (strings).
        # Yields
            Yields individual sequences.
        """

        for text in texts:
            if self.remove_stopwords:
                text = text_to_word_sequence(text, filters=self.punctuations)
                text = ' '.join([t for t in text if t not in self.stopwords])
            elif self.remove_punctuations:
                text = remove_punctuations(text, filters=self.punctuations)

            if self.lower:
                text = text.lower()
            yield ngram(text, self.ngram)




from kolibri.registry import ModulesRegistry
ModulesRegistry.add_module(CharTokenizer.name, CharTokenizer)