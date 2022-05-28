# -*- coding: utf-8 -*-
'''
Learner class
=============

The base class for all `learner` classes.
'''
from abc import abstractmethod
from typing import Any, Dict, Optional, Protocol, Tuple, TypeVar, Union

from reil import reilbase
from reil.learners.learning_rate_schedulers import (ConstantLearningRate,
                                                    LearningRateScheduler)

LabelType = TypeVar('LabelType')
InputType = TypeVar('InputType', contravariant=True)


class LearnerProtocol(Protocol[InputType, LabelType]):
    '''
    The base class for all `learner` classes.
    '''
    _learning_rate: LearningRateScheduler

    @abstractmethod
    def predict(
            self, X: Tuple[InputType, ...], training: Optional[bool] = None
    ) -> Tuple[LabelType, ...]:
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
        raise NotImplementedError

    @abstractmethod
    def learn(
            self, X: Tuple[InputType, ...], Y: Tuple[LabelType, ...],
    ) -> Dict[str, float]:
        '''
        Learn using the training set `X` and `Y`.

        Arguments
        ---------
        X:
            A list of `FeatureSet` as inputs to the learning model.

        Y:
            A list of float labels for the learning model.

        Returns
        -------
        :
            A dict of metrics.
        '''
        raise NotImplementedError

    @abstractmethod
    def get_parameters(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def set_parameters(self, parameters: Any):
        raise NotImplementedError


class Learner(reilbase.ReilBase, LearnerProtocol[InputType, LabelType]):
    '''
    The base class for all `learner` classes.
    '''
    def __init__(
            self, learning_rate: Optional[Union[
                float, LearningRateScheduler]] = None,
            **kwargs: Any) -> None:
        '''
        Arguments
        ---------
        learning_rate:
            A `LearningRateScheduler` object that determines the learning rate
            based on iteration. If any scheduler other than constant is
            provided, the model uses the `new_rate` method of the scheduler to
            determine the learning rate at each iteration.
        '''
        super().__init__(**kwargs)
        if learning_rate:
            if isinstance(learning_rate, float):
                self._learning_rate = ConstantLearningRate(learning_rate)
            else:
                self._learning_rate = learning_rate

    @classmethod
    def _empty_instance(cls):
        return cls(learning_rate=0.0)
