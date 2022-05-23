from kolibri.tokenizers.tokenizer import Tokenizer
from kdmt.text import split_text_to_sentences
from kdmt.dict import update

class SentenceTokenizer(Tokenizer):

    provides = ["sentences"]

    defaults = {
        "fixed": {
        },

        "tunable": {
            "multi-line": {
                "value": True,
                "type": "categorical",
                "values": [True, False]
            }
        }
    }

    def __init__(self, config={}):
        super().__init__(config)

        self.split_on_new_line=self.get_parameter("multi-line")

    def tokenize(self, text):
        sentences = split_text_to_sentences(text, self.split_on_new_line)

        return [sent.strip() for sent in sentences if len(sent.strip()) > 0]

    def transform(self, X):
        return [self.tokenize(x) for x in X]

    def update_default_hyper_parameters(self):
        self.defaults=update(self.defaults, SentenceTokenizer.defaults)
        super().update_default_hyper_parameters()


from kolibri.registry import ModulesRegistry
ModulesRegistry.add_module(SentenceTokenizer.name, SentenceTokenizer)

