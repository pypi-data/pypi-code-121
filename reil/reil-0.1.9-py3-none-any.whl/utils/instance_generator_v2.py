# -*- coding: utf-8 -*-
'''
InstanceGenerator class
=======================

`InstanceGenerator` takes any object derived form `ReilBase` and returns
an iterator.
'''

from __future__ import annotations

from typing import (Any, Callable, Dict, Generic, Iterable, Iterator, Optional,
                    Tuple, Type, TypeVar, Union)

from reil import reilbase, stateful
from reil.datatypes.feature_array_dumper import FeatureSetDumper
from reil.datatypes.mock_statistic import MockStatistic

T = TypeVar('T', bound=stateful.Stateful)


class InstanceGeneratorV2(Generic[T], reilbase.ReilBase):
    '''
    Make any ReilBase object an iterable.

    The initializer accepts, among other arguments, a class to generate
    instances from, and its arguments that can be fixed or functional.
    If functional, the function should accept no arguments and generate
    value for that specific argument each time it is called.
    '''

    def __init__(
            self,
            cls: Type[T],
            args_generator: Union[
                Callable[[], Tuple[int, Dict[str, Any]]],
                Iterator[Tuple[int, Dict[str, Any]]]],
            is_finite: bool = False,
            # save_instances: bool = False,
            # save_path: Union[pathlib.PurePath, str] = '',
            instance_name_pattern: str = '{n:04}',
            state_dumper: Optional[FeatureSetDumper] = None,
            **kwargs: Any):
        '''
        Attributes
        ----------
        cls:
            A class to generate instances from.

        instance_counter_stops:
            A tuple of the instance numbers where the instance
            generator should stop. A value of -1 means infinite.

        first_instance_number:
            The number of the first instance to be generated.

        auto_rewind:
            Whether to rewind after the generator hits the last stop.

        save_instances:
            Whether to save instances of the `object` or not.

        overwrite_instances:
            Whether to overwrite instances of the `object` or not.
            This flag is useful only if `save_instances` is set to `True`.

        use_existing_instances:
            Whether try to load instances before attempting to create them.

        save_path:
            The path where instances should be saved to/ loaded from.

        filename_pattern:
            A string that uses "n" as the batch number, and is
            used for saving and loading instances.

        instance_name_pattern:
            A string that uses "n" as the instance number, and is
            used to form a dictionary of instances before dumping to a file.

        pre_generate_all:
            Whether to generate all instances at once, or per counter_stop.

        state_dumper:
            If provided, it will replace the `state._dumper` of the objects.
        '''
        super().__init__(**kwargs)

        self._cls = cls
        self._is_terminated = False

        if isinstance(args_generator, Iterable):
            def gen():
                try:
                    return next(args_generator)
                except (RuntimeError, StopIteration):
                    try:
                        next(args_generator)
                    except StopIteration:
                        self._is_terminated = True
                        raise StopIteration

                    raise

            self._args_generator = gen
        else:
            self._args_generator = args_generator

        # self._save_instances = save_instances
        # self._save_path = save_path
        self._instance_name_pattern = instance_name_pattern

        self.is_finite = is_finite
        self.statistic = MockStatistic(stateful.Stateful())

        self._state_dumper = state_dumper

    @classmethod
    def _empty_instance(cls):
        return cls(object, lambda: (1, {}))

    def __iter__(self):
        return self

    def is_terminated(self, fully: bool = True) -> bool:
        return self._is_terminated

    def __repr__(self) -> str:
        try:
            return (
                f'{self.__class__.__qualname__} '
                f'{self._cls.__class__.__qualname__} '  # type: ignore
                f'-- {self._instance_counter} --> '
                f'{self._obj.__repr__()}')
        except AttributeError:
            return self.__class__.__qualname__

    def __next__(self) -> Tuple[int, T]:
        try:
            instance_counter, args = self._args_generator()
        except (StopIteration):
            raise StopIteration

        obj = self._cls(**args)

        obj._name = self._instance_name_pattern.format(n=instance_counter)
        if self._state_dumper:
            obj.state._dumper = self._state_dumper

        self.statistic.set_object(obj)

        self._obj = obj
        self._instance_counter = instance_counter

        return instance_counter, obj

    # def __getstate__(self):
    #     state = super().__getstate__()

    #     state['_instances'] = {}
    #     if '_enumerate' in state:
    #         del state['_enumerate']

    #     return state

    # def __setstate__(self, state: Dict[str, Any]) -> None:
    #     # TODO: This is a hack! remove it after the experiments!
    #     # if 'trajectory' in state['_save_path']:
    #     #     state['_instance_counter_stops'] = [10000]
    #     #     state['_filename_pattern'] = 'batch_10000_{n:03}'
    #     super().__setstate__(state)

    #     try:
    #         self._generate_batch()
    #     except IndexError:
    #         if self._auto_rewind:
    #             self.rewind()
    #             self._generate_batch()

    #     counter = (
    #         self._instance_counter
    #         - ([0] + list(self._instance_counter_stops))[self._stops_index])

    #     for _ in range(counter):
    #         self.__next__()
