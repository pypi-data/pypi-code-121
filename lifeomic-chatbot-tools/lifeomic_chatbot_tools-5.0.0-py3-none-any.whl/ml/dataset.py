import typing as t
from abc import abstractmethod
from collections import Counter, defaultdict
from itertools import chain

from pydantic.generics import GenericModel

from lifeomic_chatbot_tools._utils import requires_extras


try:
    from sklearn.model_selection import RepeatedStratifiedKFold, train_test_split
    from sklearn.utils import resample
except ImportError:
    _has_ml_deps = False
else:
    _has_ml_deps = True


_Instance = t.TypeVar("_Instance")
_Label = t.TypeVar("_Label", bound=t.Hashable)


class LabeledDataset(GenericModel, t.Generic[_Instance, _Label]):
    """
    An abstract typed array with attached helper functions related to categorically-labeled datasets. Subclassing
    instances can be used as regular lists with indexeing, etc. The only method that needs to be implemented is
    :meth:`get_label`, which should return the label associated with an instance of this dataset.

    >>> from typing import Tuple
    ...
    ... class SentimentDataset(LabeledDataset[Tuple[str, int], int]):
    ...     def get_label(self, item):
    ...         return item[1]
    ...
    ... dataset = SentimentDataset.parse_obj(
    ...     [("I hate this", -1), ("no good", -1), ("I love this", 1), ("This is great", 1)]
    ... )
    ... dataset.labels()
    ... # [-1, 1, 1]
    ... dataset.unique_labels()
    ... # {-1, 1}
    ... train, test = next(dataset.cv(nfolds=2))
    ... # train == [('I hate this', -1), ('This is great', 1)]
    ... # test == [('no good', -1), ('I love this', 1)]
    """

    __root__: t.List[_Instance]

    @abstractmethod
    def get_label(self, item: _Instance) -> _Label:
        """
        The only method that needs to be implemented by a concrete subclass. Given an ``item`` in the dataset, returns
        the classification label for that item.
        """
        pass

    def labels(self):
        return [self.get_label(item) for item in self]

    def unique_labels(self):
        return set(self.get_label(item) for item in self)

    def get_label_distribution(self):
        """
        Counts the number of each type of label present in ``self``. The returned :class:`Counter` object can be treated
        as a dictionary e.g. ``my_label_count = counter["my_label"]``.
        """
        return Counter(self.labels())

    @requires_extras(ml=_has_ml_deps)
    def cv(
        self, nfolds: int = 5, nrepeats: int = 1, seed: int = 0
    ) -> t.Iterator[t.Tuple["LabeledDataset", "LabeledDataset"]]:
        """
        Yields train/test splits for ``nfolds`` cross-validation, stratified by label. Repeats the random splitting
        ``nrepeats`` times.
        """
        cls = self.__class__
        rskf = RepeatedStratifiedKFold(n_splits=nfolds, n_repeats=nrepeats, random_state=seed)
        for train_index, test_index in rskf.split(self, self.labels()):
            yield cls.parse_obj(self[i] for i in train_index), cls.parse_obj(self[i] for i in test_index)

    @requires_extras(ml=_has_ml_deps)
    def balance(self, seed: int = 0):
        """
        Makes a new version of ``self``, where the minority labels are upsampled to have the same number of items as the
        majority label.
        """
        cls = self.__class__
        items_by_label = defaultdict(list)
        for item in self:
            items_by_label[self.get_label(item)].append(item)
        n_majority_label = max(len(items) for items in items_by_label.values())
        upsampled = chain.from_iterable(
            resample(items, replace=True, n_samples=n_majority_label, random_state=seed)
            for items in items_by_label.values()
        )
        return cls.parse_obj(list(upsampled))

    @requires_extras(ml=_has_ml_deps)
    def split(self, test_size: t.Union[float, int, None] = None, seed: int = 0, shuffle: bool = True):
        """Returns a train/test split of ``self``, stratified by label."""
        cls = self.__class__
        train, test = train_test_split(
            self, test_size=test_size, random_state=seed, shuffle=shuffle, stratify=self.labels()
        )
        return cls.parse_obj(train), cls.parse_obj(test)

    def __iter__(self) -> t.Iterator[_Instance]:
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]

    def __setitem__(self, key, value):
        self.__root__[key] = value

    def __len__(self):
        return len(self.__root__)
