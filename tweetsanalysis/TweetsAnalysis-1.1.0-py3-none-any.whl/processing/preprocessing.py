import re
import logging

from sklearn.base import BaseEstimator, TransformerMixin
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

from TweetAnalysis.config.core import config

_logger = logging.getLogger(__name__)

# Defining regex patterns.
urlPattern = r"((http://)[^ ]*|(https://)[^ ]*|(www\.)[^ ]*)"
userPattern = '@[^\s]+'
hashtagPattern = '#[^\s]+'
alphaPattern = "[^a-z0-9<>]"
sequencePattern = r"(.)\1\1+"
seqReplacePattern = r"\1\1"

# Defining regex for emojis
smileemoji = r"[8:=;]['`\-]?[)d]+"
sademoji = r"[8:=;]['`\-]?\(+"
neutralemoji = r"[8:=;]['`\-]?[\/|l*]"
lolemoji = r"[8:=;]['`\-]?p+"



class CleanText(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.output = None

    def fit(self, X, y=None):
        return self

    def transform(self, X):

        def clean(x):
            tweet = x.lower()
            # Replace all URls with '<url>'
            tweet = re.sub(urlPattern, '<url>', tweet)
            # Replace @USERNAME to '<user>'.
            tweet = re.sub(userPattern, '<user>', tweet)

            # Replace 3 or more consecutive letters by 2 letter.
            tweet = re.sub(sequencePattern, seqReplacePattern, tweet)

            # Replace all emojis.
            tweet = re.sub(r'<3', '<heart>', tweet)
            tweet = re.sub(smileemoji, '<smile>', tweet)
            tweet = re.sub(sademoji, '<sadface>', tweet)
            tweet = re.sub(neutralemoji, '<neutralface>', tweet)
            tweet = re.sub(lolemoji, '<lolface>', tweet)

            # Remove non-alphanumeric and symbols
            tweet = re.sub(alphaPattern, ' ', tweet)

            # Adding space on either side of '/' to seperate words (After replacing URLS).
            tweet = re.sub(r'/', ' / ', tweet)

            return tweet

        X_cleaned = X.apply(clean)
        self.output = X_cleaned.copy()
        return X_cleaned


class TokenizeText(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.output = None
        self.tokenizer = Tokenizer(filters="", lower=False, oov_token="<oov>")

    def fit(self, X, y=None, vocab_length=config.model.VOCAB_LEN):
        self.tokenizer.fit_on_texts(X)
        self.tokenizer.num_words = vocab_length
        return self

    def transform(self, X):
        X_transformed = self.tokenizer.texts_to_sequences(X)
        self.output = X_transformed.copy()
        return X_transformed


class PaddingText(BaseEstimator, TransformerMixin):
    def __init__(self, maxlen=config.model.INPUT_LEN):
        self.output = None
        self.maxlen = maxlen

    def fit(self, X, y=None):
        pass
        return self

    def transform(self, X):
        X_transformed = pad_sequences(X, maxlen=self.maxlen)
        self.output = X_transformed.copy()
        return X_transformed
