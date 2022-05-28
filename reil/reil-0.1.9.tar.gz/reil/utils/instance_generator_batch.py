# -*- coding: utf-8 -*-
'''
InstanceGenerator class
=======================

`InstanceGenerator` takes any object derived form `ReilBase` and returns
an iterator.
'''

from __future__ import annotations

import pathlib
import time
from copy import deepcopy
from typing import Any, Dict, Iterable, Optional, Tuple, TypeVar, Union

import dill as pickle
from reil import stateful
from reil.datatypes.feature_array_dumper import FeatureSetDumper
from reil.serialization import PickleMe
from reil.utils.instance_generator import InstanceGenerator

T = TypeVar('T', bound=stateful.Stateful)


class InstanceGeneratorBatch(InstanceGenerator[T]):
    '''
    Make any ReilBase object an iterable.

    The initializer accepts, among other arguments, an instance of an object to
    iterate, and `instance_counter_stops`, which is a tuple of the instance
    numbers where the instance generator should stop.
    '''

    def __init__(
            self,
            obj: T,
            instance_counter_stops: Tuple[int, ...] = (0,),
            first_instance_number: int = 0,
            auto_rewind: bool = False,
            save_instances: bool = False,
            overwrite_instances: bool = False,
            use_existing_instances: bool = True,
            save_path: Union[pathlib.PurePath, str] = '',
            instance_name_pattern: str = '{n:04}',
            filename_pattern: str = '{n:04}',
            pre_generate_all: bool = False,
            state_dumper: Optional[FeatureSetDumper] = None,
            **kwargs: Any):
        '''
        Attributes
        ----------
        obj:
            An instance of an object.

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
        if min(instance_counter_stops) < 0:
            raise ValueError(
                'InstanceGenratorBatch cannot be used for infinite cases.')

        super().__init__(
            obj=obj,
            instance_counter_stops=instance_counter_stops,
            first_instance_number=first_instance_number,
            auto_rewind=auto_rewind,
            save_instances=save_instances,
            overwrite_instances=overwrite_instances,
            use_existing_instances=use_existing_instances,
            save_path=save_path,
            filename_pattern=filename_pattern,
            state_dumper=state_dumper,
            **kwargs)

        self._instance_name_pattern = instance_name_pattern
        self._pre_generate_all = pre_generate_all

        self._instances: Dict[str, T] = {}
        self._enumerate: enumerate[Tuple[str, T]] = enumerate(
            self._instances.items())

        if self._object is not None:
            self._generate_batch()

    @staticmethod
    def generate_instances(
            obj: T, from_number: int, to_number: int,
            instance_name_pattern: str) -> Dict[str, T]:
        result: Dict[str, T] = {}
        for i in range(from_number, to_number):
            name = instance_name_pattern.format(n=i)
            obj.reset()
            obj._name = name
            result[name] = deepcopy(obj)

        return result

    @classmethod
    def from_instance_list(
            cls,
            obj: T,
            instance_name_lists: Tuple[Iterable[str], ...],
            save_instances: bool = False,
            overwrite_instances: bool = False,
            use_existing_instances: bool = True,
            save_path: Union[pathlib.PurePath, str] = '',
            auto_rewind: bool = False,
            state_dumper: Optional[FeatureSetDumper] = None,
            **kwargs: Any) -> InstanceGeneratorBatch[T]:
        raise NotImplementedError('Use `InstanceGenerator` instead.')

    def __next__(self) -> Tuple[int, T]:
        try:
            self._instance_counter, obj_instance = next(self._enumerate)
        except StopIteration:
            self._stops_index += 1
            self._partially_terminated = True
            try:
                self._generate_batch()
            except IndexError:
                if self._auto_rewind:
                    self.rewind()
                    self._generate_batch()

            raise

        self._partially_terminated = False
        self._object = obj_instance[1]
        self.statistic.set_object(self._object)
        if self._state_dumper:
            self._object.state._dumper = self._state_dumper

        return self._instance_counter, self._object

    def _get_end(self):
        try:
            end = self._instance_counter_stops[self._stops_index]
        except IndexError:
            if self._auto_rewind:
                self.rewind()
                end = self._instance_counter_stops[self._stops_index]
            else:
                raise StopIteration
        return end

    def _generate_batch(self):
        new_instance: bool = True
        self._instances = {}
        from_number = (
            self._first_instance_number if self._stops_index == 0
            else self._instance_counter_stops[self._stops_index - 1])
        # generates `IndexError` in case we run out of counter_stops.
        to_number = self._instance_counter_stops[self._stops_index]
        pickler = PickleMe.get('pbz2' if self._save_zipped else 'pkl')

        if self._use_existing_instances:
            for _ in range(6):
                try:
                    self._instances = pickler.load(
                        filename=self._filename_pattern.format(
                            n=self._stops_index),
                        path=self._save_path)
                    new_instance = False
                except FileNotFoundError:
                    break
                except (EOFError, OSError, pickle.UnpicklingError):
                    self._logger.info(
                        'Ran into an issue while loading! '
                        'Waiting for 20 secs.')
                    time.sleep(20)
                else:
                    file_count = len(self._instances)
                    expected_count = to_number - from_number
                    if (file_count != expected_count):
                        raise RuntimeError(
                            f'The loaded file has {file_count} instances, '
                            f'while expected {expected_count}.')

                    expected_name = self._instance_name_pattern.format(
                        n=from_number)

                    if (first := next(iter(self._instances))) != expected_name:
                        raise ValueError(
                            f'The first loaded instance is {first}, '
                            f'expected {expected_name}.')
                    break

        if not self._instances:
            self._instances = self.generate_instances(
                self._object, from_number, to_number,
                self._instance_name_pattern)

        if self._save_instances and (
                self._overwrite_instances or new_instance):
            pickler.dump(
                obj=self._instances,
                filename=self._filename_pattern.format(n=self._stops_index),
                path=self._save_path)
        self._enumerate = enumerate(self._instances.items(), from_number)

    def __getstate__(self):
        state = super().__getstate__()

        state['_instances'] = {}
        if '_enumerate' in state:
            del state['_enumerate']

        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        # TODO: This is a hack! remove it after the experiments!
        # if 'trajectory' in state['_save_path']:
        #     state['_instance_counter_stops'] = [10000]
        #     state['_filename_pattern'] = 'batch_10000_{n:03}'
        super().__setstate__(state)

        try:
            self._generate_batch()
        except IndexError:
            if self._auto_rewind:
                self.rewind()
                self._generate_batch()

        counter = (
            self._instance_counter
            - ([0] + list(self._instance_counter_stops))[self._stops_index])

        for _ in range(counter):
            self.__next__()
