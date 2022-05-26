"""
Script to train the LSTM Learner on the test and validation captions and images.
"""

import os

from models.LSTM_learner import LSTMLearner
from trainers.LSTM_trainer import LSTMTrainer
from data_utils.save_and_load_data import load_representations_captions_images
from config.core import config


if __name__ == "__main__":

    # Load data
    (
        representations_train,
        captions_train,
        _,
    ) = load_representations_captions_images("train")
    representations_val, captions_val, _ = load_representations_captions_images("val")

    representations_train = representations_train[:100]
    captions_train = captions_train[:100]

    # remove last stopword from each caption
    training_data = (
        [
            representations_train,
            captions_train[:, :-1],
        ],
        captions_train,
    )
    validation_data = (
        [representations_val, captions_val[:, :-1]],
        captions_val,
    )

    print("Training model from scratch...")
    model = LSTMLearner(max_caption_length = config.max_caption_length, num_unique_words=config.num_unique_words)
    trainer = LSTMTrainer(
        model=model,
        training_data=training_data,
        validation_data=validation_data,
        model_checkpoint_callback=False,
    )
    model = trainer.train()

    print("Saving model weights...")
    model.save_weights(
        os.path.join(config.model_folder, config.filenames.model_weights)
    )

    print("Evaluating model...")
    trainer.evaluate()
