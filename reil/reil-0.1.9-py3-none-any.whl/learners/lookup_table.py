# -*- coding: utf-8 -*-
'''
LookupTable and QLookupTable classes
====================================

`LookupTable` is a simple lookup table based on `dict` that checks for the
type of inputs to be `TableEntry`.

`QLookupTable` is a lookup table for `Q-learning`.
'''
import dataclasses
from typing import Any, Dict, Generic, Hashable, Optional, Tuple, TypeVar, Union

from reil.datatypes.feature import FeatureSet
from reil.learners.learner import Learner
from reil.learners.learning_rate_schedulers import (ConstantLearningRate,
                                                    LearningRateScheduler)

T = TypeVar('T')

# TODO: implement `load` and `save`


@dataclasses.dataclass
class TableEntry(Generic[T]):
    value: T
    N: int = 0


class LookupTable(Dict[Any, TableEntry[T]]):
    '''
    A simple lookup table based on `dict` that checks for the type of inputs
    to be `TableEntry`.
    '''
    def __setitem__(self, key: Hashable, item: Any):
        if isinstance(item, TableEntry):
            super().__setitem__(key, item)  # type: ignore
        else:
            raise TypeError('item should be of type TableEntry.')


class QLookupTable(Learner[FeatureSet, float]):
    '''
    A Q-learning lookup table class.

    This class stores input data and the corresponding output as a dictionay.
    '''
    def __init__(
            self,
            learning_rate: Union[float, LearningRateScheduler],
            initial_estimate: float = 0.0,
            minimum_visits: int = 0) -> None:
        '''
        Arguments
        ---------
        learning_rate:
            A `LearningRateScheduler` object that determines the
        learning rate of this learner.

        initial_estimate:
            The value to be returned if not enough observations
        have been collected for a given x.

        minimum_visits:
            For a given input `x`, if it was learned for more than
        `minimum_visits`, the computed estimate is returned. For any less
        visited `x`, `initial_estimate` will be returned.
        '''
        if isinstance(learning_rate, float):
            self._learning_rate = ConstantLearningRate(learning_rate)
        else:
            self._learning_rate = learning_rate
        self._initial_estimate = initial_estimate
        self._minimum_visits = minimum_visits
        # defaultdict is not efficient.
        # It creates entries as soon as they are looked up.
        self._table: LookupTable[float] = LookupTable()

    def predict(
            self, X: Tuple[FeatureSet, ...], training: Optional[bool] = None
    ) -> Tuple[float, ...]:
        '''
        predict `y` for a given input list `X`.

        Arguments
        ---------
        X:
            A list of `FeatureSet` as inputs to the prediction model.

        training:
            Whether the learner is in training mode. (Default = None)

        Returns
        -------
        :
            The predicted `y`.
        '''
        dummy = TableEntry(self._initial_estimate)
        result = tuple(float(
            self._table.get(Xi, dummy).value
            if self._table.get(Xi, dummy).N >= self._minimum_visits
            else self._initial_estimate)
            for Xi in X)

        return result

    def learn(
            self, X: Tuple[FeatureSet, ...], Y: Tuple[float, ...],
            ) -> Dict[str, float]:
        '''
        Learn using the training set `X` and `Y`.

        Arguments
        ---------
        X:
            A list of `FeatureSet` as inputs to the learning model.

        Y:
            A list of float labels for the learning model.
        '''
        for i, Xi in enumerate(X):
            if Xi not in self._table:
                self._table[Xi] = TableEntry(self._initial_estimate)

            self._table[Xi].value += self._learning_rate.initial_lr * \
                (Y[i] - self._table[Xi].value)
            self._table[Xi].N += 1

        return {}

    # def load(self, filename: str,
    #          path: Optional[Union[str, pathlib.PurePath]] = None) -> None:
    #     temp = defaultdict(
    #         lambda: {'value': self._initial_estimate,
    #                  'N': 0})
    #     _path = pathlib.Path(path if path is not None else '')
    #     with open(_path / f'{filename}.csv', 'r') as f:
    #         for k, v in csv.DictReader(f):
    #             temp[k] = v

    # def save(self,
    #          filename: str,
    #          path: Optional[Union[str, pathlib.PurePath]] = None
    #          ) -> Tuple[pathlib.PurePath, str]:
    #     _path = pathlib.Path(path if path is not None else '')
    #     with open(_path / f'{filename}.csv', 'w') as f:
    #         w = csv.writer(f)
    #         w.writerows(self._table.items())

    #     return _path, filename
