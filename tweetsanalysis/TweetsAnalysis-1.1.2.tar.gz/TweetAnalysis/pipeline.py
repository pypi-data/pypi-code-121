from sklearn.pipeline import Pipeline

from TweetAnalysis.processing import preprocessing as pp
from TweetAnalysis import model


pipe_rnn = Pipeline([
    ('tokenize', pp.TokenizeText()),
    ('pad', pp.PaddingText()),
    ('model', model.lstm_clf)
])
