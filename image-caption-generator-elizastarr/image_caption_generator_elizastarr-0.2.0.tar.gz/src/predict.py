"""
Script to predict captions using
    1) a decoder with the LSTM learner weights and
    2) test image representations.
Predictions are saved in the data/processed directory in word format (not index).
"""

import os
import argparse

from src.data_utils.save_and_load_data import (
    load_representations_captions_images,
    load_predictions,
    load_idx_word_dicts,
    save_predictions,
)
from src.data_utils.caption_preprocessing import map_idx_to_word
from src.analysis_utils.bleu_scores import get_bleu_scores
from src.analysis_utils.visualization import (
    show_10_images_and_captions_grid,
    bleu_score_histogram,
)
from models.decoder import Decoder
from config.core import config

if __name__ == "__main__":

    # Load data
    (
        image_representations_test,
        captions_test,
        images_test,
    ) = load_representations_captions_images("test")
    idx_to_word, _ = load_idx_word_dicts()
    captions_word = map_idx_to_word(captions_test, idx_to_word)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--load",
        help="Load predictions from data/ folder instead of predicting",
        action="store_true",
    )
    args = parser.parse_args()

    if args.load:
        print("Loading predictions from data/ folder.")
        predictions = load_predictions()
    else:
        print("Retrieving predictions from decoder.")
        print("Loading decoder weights...")
        decoder = Decoder()
        decoder.build(input_shape=(5000, 20480))
        decoder.load_weights(
            os.path.join(config.model_folder, config.filenames.model_weights),
            by_name=True,
            skip_mismatch=True,
        )

        print("Getting predictions from decoder...")
        predictions_idx = decoder.predict(image_representations_test)
        predictions_word = map_idx_to_word(predictions_idx, idx_to_word)

        print("Saving predictions...")
        save_predictions(predictions_word)

    # Calculate BLEU scores
    independent_bleu_scores = get_bleu_scores(
        captions_word, predictions_word, smoothing=1, independent=True
    )
    print(
        "Independent BLEU score example: {}".format(independent_bleu_scores.iloc[0, :])
    )
    bleu_score_histogram(independent_bleu_scores)
    show_10_images_and_captions_grid(images_test, predictions_word, encoded=False)
