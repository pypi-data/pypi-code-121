"""
Tokenizer Interface
"""

from kolibri.core.component import Component
from kolibri.stopwords import get_stop_words
from kdmt.dict import update
import unicodedata

class Tokenizer(Component):
    provides = ["tokens"]
    component_type="transformer"
    defaults={
        "fixed": {
            "remove-stopwords": False,
            "do-lower-case": False,
            "remove-punctuation" : False,
            "custom-stopwords": None,
            "add-to-stopwords": None,
            "remove-from-stopwords": None,
            "normalize": True,
            "remove-numbers": False,
            "filters": "!\"’«#$%&()*+,-./:;<=>?@[\\]^_`'{|}~\t\n",
        },
        "tunable": {
        }
    }

    def __init__(self, parameters={}):

        super().__init__(parameters)

        self.stopwords = None
        self.remove_stopwords = self.get_parameter("remove-stopwords")
        self.filters=self.get_parameter("filters")
        if self.remove_stopwords:
            self.stopwords = set(get_stop_words(self.get_parameter('language')))
            if isinstance(self.hyperparameters["fixed"]["add-to-stopwords"], list):
                self.stopwords = list(self.stopwords)
                self.stopwords.extend(list(self.get_parameter("add-to-stopwords")))
                self.stopwords = set(self.stopwords)
            if isinstance(self.get_parameter("remove-from-stopwords"), list):
                self.stopwords = set(
                    [sw for sw in list(self.stopwords) if sw not in self.get_parameter("remove-from-stopwords")])
        if isinstance(self.get_parameter("custom-stopwords"), list):
            self.stopwords = set(self.get_parameter("custom-stopwords"))
        self.tokenizer = None


    def update_default_hyper_parameters(self):
        self.defaults=update(self.defaults, Tokenizer.defaults)
        super().update_default_hyper_parameters()



    def tokenize(self, text):

        if self.get_parameter("do-lower-case"):
            text=text.casefold()
        if self.get_parameter("normalize"):
            text = unicodedata.normalize('NFC', str(text))
        if self.get_parameter("remove-punctuation") :
            text = "".join([ch for ch in text if ch not in self.filters])

        return text
