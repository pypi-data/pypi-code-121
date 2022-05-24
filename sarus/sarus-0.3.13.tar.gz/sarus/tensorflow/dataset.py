from __future__ import annotations  # noqa: F407

import logging
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

import tensorflow as tf

Transform = Tuple[str, Dict[str, Any]]


class Dataset:
    """A class allowing to manipulate a Sarus dataset as a Tensorflow dataset.

    The `sarus.tensorflow.Dataset` class allows to manipulate a Sarus Dataset as
    if it were a `tensorflow.data.Dataset` instance.

    Similarly to a Sarus Dataset, a `sarus.tensorflow.Dataset` uses synthetic
    data locally, which enables interactions with the data while preserving
    privacy. This allows data practitionners to design their processing
    pipelines and ML models locally as if they were working with a tensorflow
    dataset.

    Under the hood, the class memorizes the transformations that will be applied
    to the private dataset when training it remotely with differential privacy.

    Note: Only pure processing functions should be used for DP reasons.
    """

    def __init__(
        self,
        dataset,
        max_download_size: Optional[int] = None,
        original: bool = False,
    ) -> None:
        self.dataset = dataset
        self.max_download_size = max_download_size
        self.original = original

    def map(
        self,
        map_func: Callable,
        num_parallel_calls: Optional[int] = None,
        deterministic: Optional[bool] = None,
    ) -> Dataset:
        """Map `map_func` across the elements of the dataset.

        This transformation applies `map_func` to each element of this
        dataset, and returns a new dataset containing the transformed
        elements, in the same order as they appeared in the input. `map_func`
        can be used to change both the values and the structure of a dataset's
        elements. Supported structure constructs are documented `here
        <https://www.tensorflow.org/guide/data#dataset_structure>`_.
        For example, `map` can be used for adding 1 to each element, or
        projecting a subset of element components.

        >>> sarus_tf_dataset = sarus_dataset.as_tensorflow()  # ==> [ 1, 2, 3, 4, 5 ]
        >>> sarus_tf_dataset = sarus_tf_dataset.map(lambda x: x + 1)
        >>> list(sarus_tf_dataset.as_numpy_iterator())
        [2, 3, 4, 5, 6]

        The input signature of `map_func` is determined by the structure of each
        element in this dataset. For more information on `map` please refer to the
        `Tensorflow documentation <https://www.tensorflow.org/api_docs/python/tf/data/Dataset#map>`_.

        >>> sarus_tf_dataset = sarus_dataset.as_tensorflow()  # ==> range(5)
        >>> # `map_func` takes a single argument of type `tf.Tensor` with the same
        >>> # shape and dtype.
        >>> result = dataset.map(lambda x: x + 1)

        >>> # Each element is a tuple containing two `tf.Tensor` objects.
        >>> # elements = [(1, "foo"), (2, "bar"), (3, "baz")]
        >>> # `map_func` takes two arguments of type `tf.Tensor`. This function
        >>> # projects out just the first component.
        >>> sarus_tf_dataset = sarus_tf_dataset.map(lambda x_int, y_str: x_int)
        >>> list(sarus_tf_dataset.as_numpy_iterator())
        [1, 2, 3]

        >>> # Each element is a dictionary mapping strings to `tf.Tensor` objects.
        >>> # elements =  ([{"a": 1, "b": "foo"},
        ... #              {"a": 2, "b": "bar"},
        ... #              {"a": 3, "b": "baz"}])
        >>> # `map_func` takes a single argument of type `dict` with the same keys
        >>> # as the elements.
        >>> sarus_tf_dataset = sarus_tf_dataset.map(lambda d: str(d["a"]) + d["b"])

        Args:

        map_func:
            A function mapping a dataset element to another dataset element.

        num_parallel_calls:
            (Optional) A `tf.int64` scalar `tf.Tensor`,
            representing the number elements to process asynchronously in parallel.
            If not specified, elements will be processed sequentially. If the value
            `tf.data.AUTOTUNE` is used, then the number of parallel
            calls is set dynamically based on available CPU.

        deterministic:
            (Optional) When `num_parallel_calls` is specified, if this
            boolean is specified (`True` or `False`), it controls the order in which
            the transformation produces elements. If set to `False`, the
            transformation is allowed to yield elements out of order to trade
            determinism for performance. If not specified, the
            `tf.data.Options.experimental_deterministic` option
            (`True` by default) controls the behavior.

        Returns:
            sarus.tensorflow.Dataset: A `sarus.tensorflow.Dataset`.
        """
        transform = (
            "map",
            {
                "map_func": map_func,
                "num_parallel_calls": num_parallel_calls,
                "deterministic": deterministic,
            },
        )
        new_dataset = self.dataset._add_transform(transform)
        return Dataset(new_dataset, self.max_download_size, self.original)

    def unbatch(self) -> Dataset:
        """Split elements of a dataset into multiple elements.

        For example, if elements of the dataset are shaped `[B, a0, a1, ...]`,
        where `B` may vary for each input element, then for each element in the
        dataset, the unbatched dataset will contain `B` consecutive elements
        of shape `[a0, a1, ...]`.

        >>> sarus_tf_dataset = sarus_dataset.as_tensorflow()
        >>> print(next(iter(sarus_tf_dataset)).take(3))
        [ [1, 2, 3], [1, 2], [1, 2, 3, 4] ]
        >>> sarus_tf_dataset = sarus_tf_dataset.unbatch()
        >>> print(next(iter(sarus_tf_dataset)).take(9))
        [1, 2, 3, 1, 2, 1, 2, 3, 4]

        Note: `unbatch` requires a data copy to slice up the batched tensor into
        smaller unbatched tensors. When optimizing performance, try to avoid
        unnecessary usage of `unbatch`.

        Returns:
            sarus.tensorflow.Dataset: A `sarus.tensorflow.Dataset`.
        """
        transform: Transform = ("unbatch", {})
        new_dataset = self.dataset._add_transform(transform)
        return Dataset(new_dataset, self.max_download_size, self.original)

    def batch(
        self,
        batch_size: int,
        drop_remainder: bool = True,
        num_parallel_calls: Optional[int] = None,
        deterministic: Optional[bool] = None,
    ) -> Dataset:
        """Combine consecutive elements of this dataset into batches.

        >>> sarus_tf_dataset = sarus_dataset.as_tensorflow()
        >>> sarus_tf_dataset = sarus_tf_dataset.batch(3)

        The components of the resulting element will have an additional outer
        dimension, which will be `batch_size`.
        Currently, `drop_remainder`can only take True value for now.
        If you set the value to False, it will be reset to True.

        For remote private training, the dataset can be batched only once.
        Better performance is obtained if the preprocessing is applied after
        batching the dataset once.

        >>> sarus_tf_dataset.map(preprocess).batch(64)  # poor performance
        >>> sarus_tf_dataset.batch(64).map(preprocess)  # optimal performance
        >>> sarus_tf_dataset.batch(32).batch(32)  # error, not allowed
        >>> sarus_tf_dataset.map(preprocess)  # allowed but slow

        Args:

        batch_size:
            A `tf.int64` scalar `tf.Tensor`, representing the number of
            consecutive elements of this dataset to combine in a single batch.

        drop_remainder:
            (Optional) A `tf.bool` scalar `tf.Tensor`, representing whether the
            last batch should be dropped in the case it has fewer than
            `batch_size` elements; Currently, only a value of True is accepted
            for now. If you set the value to False, it will be reset to True.

        num_parallel_calls:
            (Optional) A `tf.int64` scalar `tf.Tensor`, representing the number
            of batches to compute asynchronously in parallel. If not specified,
            batches will be computed sequentially. If the value
            `tf.data.AUTOTUNE` is used, then the number of parallel calls is set
            dynamically based on available resources.

        deterministic:
            (Optional) When `num_parallel_calls` is specified, if this boolean
            is specified (`True` or `False`), it controls the order in which the
            transformation produces elements. If set to `False`, the
            transformation is allowed to yield elements out of order to trade
            determinism for performance. If not specified, the
            `tf.data.Options.experimental_deterministic` option (`True` by
            default) controls the behavior.

        Returns:
            sarus.tensorflow.Dataset: A `sarus.tensorflow.Dataset`.
        """
        # TODO `drop_remainder` = False not supported yet
        if drop_remainder is False:
            logging.info(
                "Changing `drop_remainder` to True as setting it to False "
                "is not supported yet."
            )
            drop_remainder = True

        transform = (
            "batch",
            {
                "batch_size": batch_size,
                "drop_remainder": drop_remainder,
                "num_parallel_calls": num_parallel_calls,
                "deterministic": deterministic,
            },
        )
        new_dataset = self.dataset._add_transform(transform)
        return Dataset(new_dataset, self.max_download_size, self.original)

    def filter(self, predicate: Callable) -> Dataset:
        """Filter the dataset according to `predicate`.

        >>> sarus_tf_dataset = sarus_dataset.as_tensorflow() # ==> [1, 2, 3]
        >>> sarus_tf_dataset = sarus_tf_dataset.filter(lambda x: x < 3)
        >>> list(sarus_tf_dataset.as_numpy_iterator())
        [1, 2]

        >>> # `tf.math.equal(x, y)` is required for equality comparison
        >>> def filter_fn(x):
        ...   return tf.math.equal(x, 1)
        >>> sarus_tf_dataset = sarus_tf_dataset.filter(filter_fn)
        >>> list(sarus_tf_dataset.as_numpy_iterator())
        [1]

        Args:
        predicate:
            A function mapping a dataset element to a boolean.

        Returns:
            sarus.tensorflow.Dataset: The `sarus.tensorflow.Dataset` containing
            the elements of the dataset for which `predicate` is `True`.
        """
        transform = ("filter", {"predicate": predicate})
        new_dataset = self.dataset._add_transform(transform)
        return Dataset(new_dataset, self.max_download_size, self.original)

    def _tensorflow(self) -> tf.data.Dataset:
        ds = self.dataset._synthetic_as_tf_dataset(
            batch_size=1,
            rows_number=self.max_download_size,
            original=self.original,
        )
        return _apply_transforms(ds, self.dataset.transforms)

    def __iter__(self) -> Iterator:
        return self._tensorflow().__iter__()


def _apply_transforms(
    ds: tf.data.Dataset, transforms: List[Transform]
) -> tf.data.Dataset:
    for name, params in transforms:
        if name == "map":
            ds = ds.map(**params)
        elif name == "unbatch":
            ds = ds.unbatch(**params)
        elif name == "batch":
            ds = ds.batch(**params)
        elif name == "filter":
            ds = ds.filter(**params)
        elif name == "split":
            size = params["end"] - params["start"]
            ds = ds.skip(params["start"]).take(size)
    return ds
