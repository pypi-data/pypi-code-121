import os

import pickle
from typing import List, Tuple
import numpy as np
from config.core import config


"""
Savers
"""


def save_representations_captions_images(
    image_representations: np.ndarray,
    captions: List[List],
    images: np.ndarray,
    stage: str,
) -> None:
    if stage not in ["train", "val", "test"]:
        raise ValueError(f"Stage must be either train, val, or test, not {stage}")

    (
        representations_filename,
        captions_filename,
        images_filename,
    ) = get_representation_caption_image_filenames(stage)

    pickle.dump(
        image_representations,
        open(os.path.join(config.output_filepath, representations_filename), "wb"),
    )
    pickle.dump(
        captions, open(os.path.join(config.output_filepath, captions_filename), "wb")
    )
    pickle.dump(
        images, open(os.path.join(config.output_filepath, images_filename), "wb")
    )


def save_idx_word_dicts(idx_to_word: dict, word_to_idx: dict) -> None:
    pickle.dump(
        idx_to_word,
        open(os.path.join(config.output_filepath, config.filenames.idx_to_word), "wb"),
    )
    pickle.dump(
        word_to_idx,
        open(os.path.join(config.output_filepath, config.filenames.word_to_idx), "wb"),
    )


def save_predictions(predictions_word: List[List]) -> None:
    pickle.dump(
        predictions_word,
        open(os.path.join(config.output_filepath, config.filenames.predictions), "wb"),
    )


"""
Loaders
"""


def load_raw() -> Tuple[np.ndarray, List[List]]:
    images, captions = pickle.load(
        open(os.path.join(config.input_filepath, config.filenames.raw_data), "rb")
    )
    return images, captions


def load_representations_captions_images(
    stage: str,
) -> Tuple[np.ndarray, List[List], np.ndarray]:
    if stage not in ["train", "val", "test"]:
        raise ValueError(f"Stage must be either train, val, or test, not {stage}")

    (
        representations_filename,
        captions_filename,
        images_filename,
    ) = get_representation_caption_image_filenames(stage)

    image_representations = pickle.load(
        open(os.path.join(config.output_filepath, representations_filename), "rb")
    )
    captions = pickle.load(
        open(os.path.join(config.output_filepath, captions_filename), "rb")
    )
    images = pickle.load(
        open(os.path.join(config.output_filepath, images_filename), "rb")
    )
    return image_representations, captions, images


def load_idx_word_dicts() -> Tuple[dict, dict]:
    idx_to_word = pickle.load(
        open(os.path.join(config.output_filepath, config.filenames.idx_to_word), "rb")
    )
    word_to_inx = pickle.load(
        open(os.path.join(config.output_filepath, config.filenames.word_to_idx), "rb")
    )
    return idx_to_word, word_to_inx


def load_predictions() -> List:
    predictions = pickle.load(
        open(os.path.join(config.output_filepath, config.filenames.predictions), "rb")
    )
    return predictions


"""
Helper Functions
"""


def get_representation_caption_image_filenames(stage: str):
    representations_filename = config.filenames.representations.replace("stage", stage)
    captions_filename = config.filenames.captions.replace("stage", stage)
    images_filename = config.filenames.images.replace("stage", stage)
    return representations_filename, captions_filename, images_filename
