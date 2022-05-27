import numpy as np

from TweetAnalysis.processing import data_management as dm
from TweetAnalysis.processing import preprocessing as pp
from TweetAnalysis.config.core import config
from TweetAnalysis import pipeline
from TweetAnalysis import word_embeddings


def run_training(save_result: bool = True):
    """Train a Recurrent Neural Network."""

    df = dm.read_data()[:100000]
    X, y = dm.get_value_target(df)

    print('cleaning for training...')
    clean_text = pp.CleanText()
    X_cleaned = clean_text.transform(X)

    print('training word embeddings...')
    embedding_matrix = word_embeddings._Word2Vec().make_embedding_matrix(X_cleaned)
    pipeline.pipe_rnn.named_steps['model'].set_params(
        embedding_matrix=embedding_matrix)

    print('training RNN model...')
    pipeline.pipe_rnn.fit(X_cleaned, y)

    if save_result:
        dm.save_pipeline_keras(pipeline.pipe_rnn)


if __name__ == '__main__':
    run_training(save_result=True)
