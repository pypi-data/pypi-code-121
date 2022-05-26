import operator
from typing import Dict, List, Tuple

from src.data_utils.save_and_load_data import load_idx_word_dicts


def get_caption_dictionaries(captions: List[List]) -> Tuple[dict, dict, int, int, int]:
    """Analyzes the captions and returns metadata.
       Maps words to integers according to their frequency.
       Stop character "_" is the most frequent and assigned integer 0.

    Parameters
    ----------
    captions : List[List]
        A list containing a list of 5 captions for each image.

    Returns
    -------
    Tuple[dict,dict,int,int,int]
        Integer to word mapping, word to integer mapping, length of the longest caption,
        total number of words, number of unique words
    """
    # initialize counters and frequency dictionary
    max_caption_length = 0
    total_words = len(captions) * 5  # one stop character per caption
    num_unique_words = 1  # including the stop character
    word_frequecies = {}

    for image_captions in captions:  # for each image's set of captions
        for caption in image_captions:  # image_cations contains 5 captions
            if len(caption) > max_caption_length:
                max_caption_length = len(caption)
            for word in caption:
                if word in word_frequecies:
                    word_frequecies[word] += 1
                else:  # new word
                    num_unique_words += 1
                    word_frequecies[word] = 1
                total_words += 1

    # most frequent words first
    sorted_word_freqs = sorted(
        word_frequecies.items(), key=operator.itemgetter(1), reverse=True
    )

    # create word to index dictionary
    word_to_idx = {"_": 0}  # "_" is the stop character
    index = 1
    for word, _ in sorted_word_freqs:
        word_to_idx[word] = index
        index += 1

    # flip keys and values
    idx_to_word = dict((v, k) for (k, v) in word_to_idx.items())

    return idx_to_word, word_to_idx, max_caption_length, total_words, num_unique_words


def map_idx_to_word(captions_idx: List[List], idx_to_word: Dict) -> List[List]:
    captions_word = [
        [idx_to_word.get(key) for key in caption] for caption in captions_idx
    ]
    return captions_word
