import os
from glob import glob
from typing import Any
from typing import Iterable, Iterator

import numpy as np
import tensorflow as tf
from tensorflow import keras

from kolibri.indexers.multi_content_indexer import MultiContentIndexer
from kolibri.indexers.multi_target_indexer import MultiTargetIndexer


class DataGenerator(keras.utils.Sequence):

    def __init__(self, x_values, y_values, content_indexer=None, label_indexer=None, x_augmentor=None, batch_size=1,
                 shuffle=False):
        self.y_values = y_values  # array of y_values
        self.x_values = x_values  # array of image paths
        self.batch_size = batch_size  # batch size
        self.shuffle = shuffle  # shuffle bool
        self.on_epoch_end()
        self.content_indexer = content_indexer
        self.label_indexer = label_indexer
        self.augmentor = x_augmentor

    def __len__(self):
        'Denotes the number of batches per epoch'

        if self.x_values is not None:
            return max(1, int(np.ceil(len(self.x_values) / self.batch_size)))
        else:
            return max(1, int(np.ceil(len(self.y_values) / self.batch_size)))

    def set_batch_size(self, new_batch_size):
        self.batch_size = new_batch_size

    def on_epoch_end(self):
        'Updates indexes after each epoch'
        if self.x_values is not None:
            self.indexes = np.arange(len(self.x_values))
        else:
            self.indexes = np.arange(len(self.y_values))

        if self.shuffle:
            np.random.shuffle(self.indexes)

    def __getitem__(self, index):
        'Generate one batch of texts'
        # selects indices of texts for next batch
        indexes = self.indexes[index * self.batch_size: (index + 1) * self.batch_size]

        # select texts and load images
        labels = None
        content = None

        if self.y_values is not None:
            labels = np.array([self.y_values[k] for k in indexes])
            if self.label_indexer:
                labels = self.label_indexer.transform(labels)
            if self.batch_size == 1:
                if isinstance(self.label_indexer, MultiTargetIndexer):
                    labels = [l[0] for l in labels]
                else:
                    labels = labels[0]
        if self.x_values is not None:
            # preprocess and augment texts

            content = [self.x_values[k] for k in indexes]
            if self.augmentor:
                content = self.augmentor(content)

            if self.content_indexer:
                content = self.content_indexer.transform(content)

            if self.batch_size == 1:
                if isinstance(self.content_indexer, MultiContentIndexer):
                    content = [c[0] for c in content]
                else:
                    content = content[0]
        #           content = np.array(content)
        return content, labels

    def get_data(self):
        X = []
        Y = []
        batchsize = self.batch_size
        self.batch_size = 1
        if isinstance(self.content_indexer, MultiContentIndexer):
            for i in self.content_indexer.content_indexers:
                X.append([])
        if isinstance(self.label_indexer, MultiTargetIndexer):
            for i in self.label_indexer.label_indexers:
                Y.append([])

        for i in range(0, len(self.x_values)):
            if isinstance(self.content_indexer, MultiContentIndexer):
                for j in range(len(self.content_indexer.content_indexers)):
                    X[j].append(self[i][0][j])
            else:
                X.append(self[i][0])
            if isinstance(self.content_indexer, MultiContentIndexer):
                for j in range(len(self.label_indexer.label_indexers)):
                    Y[j].append(self[i][1][j])
            else:
                Y.append(self[i][1])

        self.batch_size = batchsize

        if isinstance(self.content_indexer, MultiContentIndexer):
            for i in range(len(self.content_indexer.content_indexers)):
                X[i] = np.array(X[i])
        else:
            X = np.array(X)
        if isinstance(self.label_indexer, MultiTargetIndexer):
            for i in range(len(self.label_indexer.label_indexers)):
                Y[i] = np.array(Y[i])
        else:
            Y = np.array(Y)

        return X, Y


class FolderDataGenerator(DataGenerator):

    def __init__(self, folder_path, content_indexer=None, label_indexer=None, x_augmentor=None,
                 batch_size=1, shuffle=False):
        if not os.path.exists(folder_path):
            raise Exception('(' + folder_path + ') Folder not found')
        file_paths = glob('{}/**'.format(folder_path), recursive=True)
        file_paths = [x.replace(os.sep, '/') for x in file_paths if os.path.isfile(x)]
        labels = [os.path.basename(os.path.dirname(x)) for x in file_paths]

        super().__init__(x_values=file_paths, y_values=labels, content_indexer=content_indexer,
                         label_indexer=label_indexer, x_augmentor=x_augmentor, batch_size=batch_size, shuffle=shuffle)


class Seq2SeqDataSet(Iterable):
    def __init__(self,
                 corpus,
                 *,
                 batch_size: int = 64,
                 encoder_processor,
                 decoder_processor,
                 encoder_seq_length: int = None,
                 decoder_seq_length: int = None):
        self.corpus = corpus

        self.encoder_processor = encoder_processor
        self.decoder_processor = decoder_processor

        self.encoder_seq_length = encoder_seq_length
        self.decoder_seq_length = decoder_seq_length

        self.batch_size = batch_size

    def __len__(self) -> int:
        return max(len(self.corpus) // self.batch_size, 1)

    def __iter__(self) -> Iterator:
        batch_x, batch_y = [], []
        for x, y in self.corpus:
            batch_x.append(x)
            batch_y.append(y)
            if len(batch_x) == self.batch_size:
                x_tensor = self.encoder_processor.transform(batch_x, )
                y_tensor = self.decoder_processor.transform(batch_y, )
                yield x_tensor, y_tensor
                batch_x, batch_y = [], []

    def items(self, batch_count: int = None) -> Any:
        x_shape = [self.batch_size, self.encoder_seq_length]
        y_shape = [self.batch_size, self.decoder_seq_length]
        dataset = tf.data.Dataset.from_generator(self.__iter__,
                                                 output_types=(tf.int64, tf.int64),
                                                 output_shapes=(x_shape, y_shape))
        dataset = dataset.repeat()
        dataset = dataset.prefetch(50)
        if batch_count is None:
            batch_count = len(self)
        return dataset.take(batch_count)
