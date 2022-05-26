from typing import Dict, List
import os

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.data_utils.save_and_load_data import load_idx_word_dicts


def bleu_score_histogram(bleu_scores: pd.DataFrame, file_name: str = None):
    kwargs = dict(histtype="stepfilled", alpha=0.5, bins=10)
    fig_size = plt.figure(figsize=(11, 5))

    ax1 = plt.hist(bleu_scores["BLEU-1"], **kwargs)
    ax2 = plt.hist(bleu_scores["BLEU-2"], **kwargs)
    ax3 = plt.hist(bleu_scores["BLEU-3"], **kwargs)
    ax4 = plt.hist(bleu_scores["BLEU-4"], **kwargs)

    title = plt.title("Distribution of BLEU Scores")
    title = plt.xlabel("BLEU Score")
    title = plt.ylabel("Frequency")
    xlim = plt.xlim(
        0,
    )
    legend = plt.legend(
        labels=["BLEU-1", "BLEU-2", "BLEU-3", "BLEU-4"], fontsize="x-large"
    )

    if file_name is not None:
        figure_folder = Path("reports/figures/")
        plt.savefig(os.path.join(figure_folder, file_name), dpi=300)

    plt.show()


def show_random_image_and_caption_individual(
    images: np.ndarray,
    captions: List,
    idx_to_word: Dict,
    quantity: int,
    file_name: str = None,
):
    for i in range(quantity):
        separator = ", "
        idx = np.random.randint(0, images.shape[0])

        encoded_caption = captions[idx, ...]
        encoded_caption = [k for k in encoded_caption if k >= 0]
        caption = [idx_to_word[i] for i in encoded_caption]

        plt.imshow(images[idx % images.shape[0], ...])
        formatted_caption = separator.join(caption).replace(",", "").replace("_", "")
        plt.xlabel(formatted_caption, wrap=True, fontsize=8, ha="center")

        if file_name is not None:
            print("Saving image")
            figure_folder = Path("reports/figures/")
            plt.savefig(os.path.join(figure_folder, file_name), dpi=300)

        plt.show()


def show_10_images_and_captions_grid(
    images: np.ndarray,
    captions: List,
    idx_to_word: Dict,
    encoded: bool = True,
    file_name: str = None,
):
    idxs = np.random.choice(images.shape[0], 10, replace=False)
    separator = ", "

    fig, axs = plt.subplots(5, 2, figsize=(10, 8))
    for counter, idx in enumerate(idxs, 0):
        ax = axs[counter % 5][counter % 2]
        ax.imshow(images[idx % images.shape[0], ...])

        if encoded:
            encoded_caption = captions[idx, ...]
            encoded_caption = [k for k in encoded_caption if k >= 0]
            caption = [idx_to_word[i] for i in encoded_caption]
        else:
            caption = captions[idx]

        ax.axes.xaxis.set_ticks([])
        ax.axes.yaxis.set_ticks([])
        formatted_caption = separator.join(caption).replace(",", "").replace("_", "")
        ax.set_xlabel(formatted_caption, wrap=True, fontsize=8, ha="center")

    if file_name is not None:
        figure_folder = Path("reports/figures/")
        plt.savefig(os.path.join(figure_folder, file_name), dpi=300)

    plt.show()
