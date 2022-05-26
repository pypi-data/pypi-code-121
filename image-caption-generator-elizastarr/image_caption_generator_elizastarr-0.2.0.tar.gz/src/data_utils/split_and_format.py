import os
from typing import Tuple, Union, List

import pickle
import numpy as np

from sklearn.model_selection import train_test_split
from config.core import config


def train_test_val_split(data: Union[np.ndarray, List]) -> Tuple:
    """Split input data into training, test, and validation

    Parameters
    ----------
    data : Union[np.ndarray, List]
        Image or caption input data to be split into train, test, and validation splits
    test_val_size : int (Optional)
        Number of test and validation instances
    Returns
    -------
    Tuple
        The input data split into train, test, and validation
    """

    X_train, X_test = train_test_split(
        data,
        test_size=config.test_val_size,
        random_state=config.random_state,
        shuffle=True,
    )
    X_train, X_val = train_test_split(
        X_train,
        test_size=config.test_val_size,
        random_state=config.random_state,
        shuffle=True,
    )

    return X_train, X_test, X_val


"""
format_as_matrix() mostly given by the instructor.
"""


def format_as_matrix(
    representations: np.ndarray,
    captions: List,
    max_caption_length: int,
    word_to_idx: dict,
) -> Tuple[np.ndarray, np.ndarray]:
    """

    Parameters
    ----------
    representations : np.ndarray
        Unique image representations
    captions : List
        A list containing a list of five captions per image
    max_caption_length : int
        Defines the number of columns in the label matrix
    word_to_idx : dict
        Used to encode the captions

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Image representations (each appearing 5x) and integer-encoded captions

    Raises
    ------
    AssertionError
        Different number of representations and caption groups.
    """

    # Note that there are 5 captions per image
    if representations.shape[0] != len(captions):
        raise AssertionError("Different number of representations and caption groups.")

    invalid = []
    for idx, image_captions in enumerate(captions):
        if len(image_captions) != 5:
            invalid.append(idx)
    if invalid:
        raise AssertionError(
            f"Each image must have 5 captions, but images {invalid} did not."
        )

    N = representations.shape[0]
    duplicated_representations = None
    labels = None

    for j in range(5):  # for the jth caption of all images

        # encode the words of the jth caption for all images
        current_labels = np.zeros((N, max_caption_length), dtype=np.uint32)
        for i in range(N):  # for the ith image
            for index, word in enumerate(captions[i][j]):
                current_labels[i, index] = word_to_idx[word]

        # Add image representations for the jth caption
        # Add the jth set of captions
        if duplicated_representations is None:
            duplicated_representations = representations
            labels = current_labels
        else:
            duplicated_representations = np.concatenate(
                (duplicated_representations, representations), 0
            )
            labels = np.concatenate((labels, current_labels), 0)

    return duplicated_representations, labels
