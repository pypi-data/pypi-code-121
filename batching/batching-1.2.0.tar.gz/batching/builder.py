import numpy as np
from itertools import islice, chain
from concurrent.futures import ThreadPoolExecutor

from functools import reduce
from operator import add
import logging
import time

from batching.storage import BatchStorageFile, BatchStorageMemory, BatchStorageS3
from batching.storage_meta import StorageMeta
from batching.translate import Translate


class Builder(object):
    def __init__(self,
                 storage,
                 translate,
                 batch_size=8192,
                 pseudo_stratify=False,
                 stratify_nbatch_groupings=50,
                 verbose=False,
                 seed=None,
                 n_workers=None):

        self.batch_size = batch_size
        self._stratify = pseudo_stratify
        self._stratify_max_groupings = stratify_nbatch_groupings
        self._verbose = verbose

        self._logger = logging.getLogger(__name__)
        self._n_workers = n_workers
        self._storage = storage

        self.translate = translate

        if seed:
            np.random.seed(seed)

    @property
    def storage(self):
        return self._storage

    def _generate_session_sequences(self, session_df_list):
        n_chunks = 50
        chunks = map(lambda i: islice(session_df_list, i, i + n_chunks), range(0, len(session_df_list), n_chunks))
        with ThreadPoolExecutor(max_workers=self._n_workers) as p:
            for result in chain.from_iterable(
                    map(lambda s: p.map(self.translate.scale_and_transform_session, s), chunks)):
                yield result

    def _imbalanced_minibatch_generator(self, X, y):
        n_batches = int(X.shape[0] // self.batch_size)

        # Find ratio of ones to zeros, and how many to put in each batch
        ones, zeros = np.where(y == 1)[0], np.where(y == 0)[0]
        zero_ratio = len(zeros) / float(len(ones) + len(zeros))
        zeros_per_batch = int(self.batch_size * zero_ratio)
        ones_per_batch = int(self.batch_size - zeros_per_batch)

        if self._verbose:
            self._logger.info(f"balancing {n_batches} batches {round(100 * (1 - zero_ratio), 2)}% ones")

        # randomize the indices of ones and zeros and split them into amount needed per batch
        np.random.shuffle(ones)
        np.random.shuffle(zeros)
        ones_batches = len(ones) // ones_per_batch if ones_per_batch else 0
        zeros_batches = len(zeros) // zeros_per_batch if zeros_per_batch else 0
        max_balanced_batches = min(ones_batches, zeros_batches)

        # select balanced batches
        if max_balanced_batches > 0:
            ones_idx = np.split(ones[:ones_per_batch * max_balanced_batches], max_balanced_batches)
            zeros_idx = np.split(zeros[:zeros_per_batch * max_balanced_batches], max_balanced_batches)

            for i in range(max_balanced_batches):
                selection = np.concatenate([ones_idx[i], zeros_idx[i]])
                yield (X[selection], y[selection])

        # remaining unbalanced batches
        rem_ones = (ones_per_batch * (ones_batches - max_balanced_batches) +
                    (len(ones) % ones_per_batch if ones_per_batch else 0))
        rem_zeros = ((zeros_per_batch * (zeros_batches - max_balanced_batches) +
                      (len(zeros) % zeros_per_batch if zeros_per_batch else 0)))
        selection = np.concatenate([ones[-rem_ones:], zeros[-rem_zeros:]])

        even_split = len(selection) % self.batch_size
        even_selection = selection[:-even_split] if even_split > 0 else selection
        for rem_selection in np.split(even_selection, len(even_selection) // self.batch_size):
            yield (X[rem_selection], y[rem_selection])

    def _pseudo_stratify_batches(self, session_df_list):
        X_group, y_group = [], []

        group_count = 0
        for (X_batch, y_batch) in self.generate_batches(session_df_list):
            X_group.append(X_batch)
            y_group.append(y_batch)
            group_count += 1
            if group_count >= self._stratify_max_groupings:
                for (X_balanced, y_balanced) in self._imbalanced_minibatch_generator(np.concatenate(X_group, axis=0),
                                                                                     np.concatenate(y_group, axis=0)):
                    yield (X_balanced, y_balanced)
                X_group, y_group = [], []
                group_count = 0

        # yield remaining
        for i in range(group_count):
            yield (X_group[i], y_group[i])

    def save_meta(self):
        params = {
            'batch_size': self.batch_size
        }
        params.update(self.translate.get_translate_params())
        self._storage.save_meta(params)

    def load_meta(self):
        params = self._storage.load_meta()
        self.translate.set_translate_params(params)
        self.batch_size = params["batch_size"]

    def generate_batches(self, session_df_list):
        if not session_df_list or len(session_df_list) == 0:
            raise Exception("No dataset provided")

        first = session_df_list[0].shape
        total = reduce(add, [s.shape[0] for s in session_df_list])
        dataset_shape = (total,) + first[1:]
        if self._verbose:
            self._logger.info(f"Total dataset shape {dataset_shape}")

        self.translate.normalize_dataset(session_df_list)

        X_rem = np.array([]).reshape((0, self.translate.time_steps, self.translate.num_features))
        y_rem = np.array([])

        if self._verbose:
            self._logger.info("Generating batches")
        for (X_session, y_session) in self._generate_session_sequences(session_df_list):
            X_session = np.concatenate([X_session, X_rem], axis=0)
            y_session = np.concatenate([y_session, y_rem], axis=0)

            n_batches = int(X_session.shape[0] // self.batch_size)
            remainder = X_session.shape[0] % self.batch_size

            for batch_idx in range(n_batches):
                _bin = batch_idx * self.batch_size
                X = X_session[_bin:_bin + self.batch_size]
                y = y_session[_bin:_bin + self.batch_size]
                yield (X, y)

            X_rem = X_session[-remainder:]
            y_rem = y_session[-remainder:]

    def generate_and_save_batches(self, session_df_list):
        batch_generator = self._pseudo_stratify_batches if self._stratify else self.generate_batches

        if self._verbose:
            perf_interval = 1
            start = time.perf_counter()

        for (X_batch, y_batch) in batch_generator(session_df_list):
            assert X_batch.shape[0] == self.batch_size
            assert y_batch.shape[0] == self.batch_size

            self._storage.save(X_batch, y_batch)
            if self._verbose:
                if perf_interval > 50:
                    rate = round(50 / (time.perf_counter() - start), 2)
                    self._logger.info(f"Batch production rate: {rate} batches/s")
                    start = time.perf_counter()
                    perf_interval = 0
                perf_interval += 1

        self.save_meta()

    @staticmethod
    def file_builder_factory(feature_set,
                             look_back,
                             look_forward,
                             batch_size,
                             directory=None,
                             batch_seconds=1,
                             stride=1,
                             sequence_labels=False,
                             validation_split=0,
                             pseudo_stratify=False,
                             stratify_nbatch_groupings=20,
                             n_workers=None,
                             seed=None,
                             normalize=True,
                             custom_transforms=None,
                             session_norm_filter=None,
                             verbose=False):

        storage_meta = StorageMeta(validation_split=validation_split)
        storage = BatchStorageFile(storage_meta, directory=directory)
        translate = Translate(feature_set, look_back, look_forward, batch_seconds, stride, sequence_labels,
                              normalize, verbose, custom_transforms, session_norm_filter)
        return Builder(storage=storage,
                       translate=translate,
                       batch_size=batch_size,
                       pseudo_stratify=pseudo_stratify,
                       stratify_nbatch_groupings=stratify_nbatch_groupings,
                       verbose=verbose,
                       seed=seed,
                       n_workers=n_workers)

    @staticmethod
    def memory_builder_factory(feature_set,
                               look_back,
                               look_forward,
                               batch_size,
                               batch_seconds=1,
                               stride=1,
                               sequence_labels=False,
                               validation_split=0,
                               pseudo_stratify=False,
                               stratify_nbatch_groupings=20,
                               n_workers=None,
                               seed=None,
                               normalize=True,
                               custom_transforms=None,
                               session_norm_filter=None,
                               verbose=False):

        storage_meta = StorageMeta(validation_split=validation_split)
        storage = BatchStorageMemory(storage_meta)
        translate = Translate(feature_set, look_back, look_forward, batch_seconds, stride, sequence_labels,
                              normalize, verbose, custom_transforms, session_norm_filter)
        return Builder(storage=storage,
                       translate=translate,
                       batch_size=batch_size,
                       pseudo_stratify=pseudo_stratify,
                       stratify_nbatch_groupings=stratify_nbatch_groupings,
                       verbose=verbose,
                       seed=seed,
                       n_workers=n_workers)

    @staticmethod
    def s3_builder_factory(s3_bucket_resource,
                           feature_set,
                           look_back,
                           look_forward,
                           batch_size,
                           s3_prefix="",
                           batch_seconds=1,
                           stride=1,
                           sequence_labels=False,
                           validation_split=0,
                           pseudo_stratify=False,
                           stratify_nbatch_groupings=20,
                           n_workers=None,
                           seed=None,
                           normalize=True,
                           custom_transforms=None,
                           session_norm_filter=None,
                           verbose=False):

        storage_meta = StorageMeta(validation_split=validation_split)
        storage = BatchStorageS3(storage_meta, s3_bucket_resource=s3_bucket_resource, s3_prefix=s3_prefix)
        translate = Translate(feature_set, look_back, look_forward, batch_seconds, stride, sequence_labels,
                              normalize, verbose, custom_transforms, session_norm_filter)
        return Builder(storage=storage,
                       translate=translate,
                       batch_size=batch_size,
                       pseudo_stratify=pseudo_stratify,
                       stratify_nbatch_groupings=stratify_nbatch_groupings,
                       verbose=verbose,
                       seed=seed,
                       n_workers=n_workers)
