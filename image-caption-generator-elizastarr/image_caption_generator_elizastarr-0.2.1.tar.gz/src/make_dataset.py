# -*- coding: utf-8 -*-
import os
import pickle

from data_utils.image_representations import get_image_representations
from data_utils.caption_preprocessing import get_caption_dictionaries
from data_utils.split_and_format import train_test_val_split, format_as_matrix
from data_utils.save_and_load_data import (
    save_representations_captions_images,
    save_idx_word_dicts,
    load_raw,
)
from config.core import config


def main():
    """Runs data processing scripts to turn raw data from data/raw into processed data in data/processed.

    Parameters
    ----------
    input_filepath : Path
        Path of raw input data
    output_filepath : Path
        Path to folder to save processed data
    """

    print(f"Loading data from {config.input_filepath}")
    images, captions = load_raw()
    print("images shape: ", images.shape, " captions length: ", len(captions))

    print("Retreiving image representations...")
    image_representations = get_image_representations(images)

    print("Encoding and analyzing captions...")
    (
        idx_to_word,
        word_to_idx,
        max_caption_length,
        total_words,
        num_unique_words,
    ) = get_caption_dictionaries(captions)
    print(f"Maximum caption length: {max_caption_length}.")
    print(f"{total_words} total words in the corpus.")
    print(f"{num_unique_words} unique words in the corpus.")

    assert max_caption_length == config.max_caption_length
    assert num_unique_words == config.num_unique_words

    print(f"Splitting data into train, test, and validation...")
    (
        image_representations_train,
        image_representations_test,
        image_representations_val,
    ) = train_test_val_split(image_representations)
    captions_train, captions_test, captions_val = train_test_val_split(captions)
    images_train, images_test, images_val = train_test_val_split(images)

    print(f"Reformatting image representations and captions...")
    image_representations_train, captions_train = format_as_matrix(
        image_representations_train, captions_train, max_caption_length, word_to_idx
    )
    image_representations_test, captions_test = format_as_matrix(
        image_representations_test, captions_test, max_caption_length, word_to_idx
    )
    image_representations_val, captions_val = format_as_matrix(
        image_representations_val, captions_val, max_caption_length, word_to_idx
    )

    print(f"Saving processed data to f{config.output_filepath}...")
    if not os.path.exists(config.output_filepath):
        os.makedirs(config.output_filepath)
    save_representations_captions_images(
        image_representations_train, captions_train, images_train, "train"
    )
    save_representations_captions_images(
        image_representations_val, captions_val, images_val, "val"
    )
    save_representations_captions_images(
        image_representations_test, captions_test, images_test, "test"
    )
    save_idx_word_dicts(idx_to_word=idx_to_word, word_to_idx=word_to_idx)

    print("Processing complete.")


if __name__ == "__main__":
    main()
