import tensorflow as tf
import numpy as np


def to_categorical(y, n_classes):
    return np.eye(n_classes)[y.astype(int)]


class BatchGenerator(tf.keras.utils.Sequence):
    def __init__(self, storage, is_validation, seed=None, n_classes=1, batch_split=1):
        self._storage = storage
        self._n_classes = n_classes
        self._batch_ids = storage.meta.get_ids(is_validation)
        self._is_validation = is_validation
        self._batch_split = batch_split

        self._X = None
        self._y = None
        self._id_cache = None

        if seed:
            np.random.seed(seed)

        self.indexes = None
        self.on_epoch_end()

    def __len__(self):
        """Denotes the number of batches per epoch"""
        return len(self._batch_ids) * self._batch_split

    def _split(self, index):
        n = self._X.shape[0]
        bin = index % self._batch_split

        split_duration = n / self._batch_split
        start, end = [(int(i * split_duration), int((i + 1) * split_duration)) for i in range(self._batch_split)][bin]
        return self._X[start:end], self._y[start:end]

    def __getitem__(self, index):
        """Generate one batch of data"""
        # Generate indexes of the batch
        batch_id = self.indexes[int(index // self._batch_split)]

        if batch_id != self._id_cache:
            self._X, self._y = self._storage.load(batch_id, self._is_validation)
            if self._n_classes > 1:
                self._y = to_categorical(self._y, self._n_classes)

            self._id_cache = batch_id

        return self._split(index)

    def on_epoch_end(self):
        """Updates indexes after each epoch"""
        self.indexes = self._batch_ids
        np.random.shuffle(self.indexes)
