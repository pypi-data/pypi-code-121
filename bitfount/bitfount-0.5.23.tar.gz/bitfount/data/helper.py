"""Helper functions concerning data."""

from bitfount.data.dataloaders import _BitfountDataLoader


def convert_epochs_to_steps(epochs: int, dataloader: _BitfountDataLoader) -> int:
    """Converts number of epochs into number of steps.

    Each step represents a minibatch. Ensure provided dataloader supports batching.

    Args:
        epochs: An integer denoting the epoch number.
        dataloader: An instance of a Bitfount DataLoader.

    Returns:
          An integer indicating the step number.
    """
    num_batches = len(dataloader)
    return num_batches * epochs
