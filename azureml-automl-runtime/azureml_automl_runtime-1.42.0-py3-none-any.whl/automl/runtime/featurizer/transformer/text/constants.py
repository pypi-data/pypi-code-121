# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Constants for various tranformers."""
from azureml.training.tabular.featurization.text.bagofwords_transformer import TFIDF_VECTORIZER_CONFIG


class NIMBUS_ML_PARAMS:
    """Param keys/values for NimbusML pipeline."""

    FEATURIZER_KEY = "featurizer"
    CLASSIFIER_KEY = "classifier"
    NGRAM_CHAR_WEIGHTING = "Tf"
    NGRAM_CHAR_KEY = "char_feature_extractor"  # keyword arg for NimbusML ngram char_feature_extractor
    NGRAM_CHAR_LENGTH_KEY = "ngram_char_length"
    NGRAM_CHAR_LENGTH = 3
    NGRAM_CHAR_ALL_LENGTHS = False
    NGRAM_WORD_WEIGHTING = "Tf"
    NGRAM_WORD_KEY = "word_feature_extractor"  # keyword arg for NimbusML ngram word_feature_extractor
    NGRAM_WORD_LENGTH_KEY = "ngram_word_length"
    NGRAM_WORD_LENGTH = 2
    NGRAM_WORD_ALL_LENGTHS = True
    AVG_PERCEPTRON_ITERATIONS = 10
    NIMBUS_ML_PACKAGE_NAME = "nimbusml"
