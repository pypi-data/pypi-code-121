import joblib
import numpy as np
from gensim.models import Word2Vec

from TweetAnalysis.config.core import config
from TweetAnalysis.processing import preprocessing as pp


class _Word2Vec(object):
    def __init__(self) -> None:
        None

    def make_embedding_matrix(self, X):

        # clean_text = pp.CleanText()
        # X_cleaned = clean_text.transform(X)

        tokenizer = pp.TokenizeText()
        tokenizer.fit(X)

        # Creating Word2Vec training dataset.
        Word2vec_train_data = list(map(lambda x: x.split(), X))

        # Defining the model and training it.
        word2vec_model = Word2Vec(Word2vec_train_data,
                                  vector_size=config.model.EMBEDDING_DIMENSIONS,
                                  workers=8,
                                  min_count=5)

        embedding_matrix = np.zeros(
            (config.model.VOCAB_LEN, config.model.EMBEDDING_DIMENSIONS))

        for word, token in tokenizer.tokenizer.word_index.items():
            if word2vec_model.wv.__contains__(word):
                embedding_matrix[token] = word2vec_model.wv.__getitem__(word)

        joblib.dump(embedding_matrix, config.app.MODELS_PATH + config.app.EMBEDDED_MATRIX_NAME)

        return embedding_matrix


if __name__ == '__main__':
    pass
    # make_embedding_matrix()
