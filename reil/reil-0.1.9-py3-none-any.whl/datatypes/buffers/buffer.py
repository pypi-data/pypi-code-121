# -*- coding: utf-8 -*-
'''
Buffer class
============

The base class for all buffers in `reil`.
'''

from typing import (Callable, Dict, Generic, List, Literal, Optional, Tuple, TypeVar,
                    Union)

import numpy as np
from reil import reilbase

T1 = TypeVar('T1')
T2 = TypeVar('T2')

PickModes = Literal['all', 'random', 'recent', 'old']
Funcs = Literal['sum', 'min', 'max', 'mean']

class Buffer(reilbase.ReilBase, Generic[T1, T2]):
    '''
    The base class for all buffers in `reil`.
    '''

    def __init__(
            self,
            buffer_size: Optional[int] = None,
            buffer_names: Optional[List[str]] = None,
            pick_mode: Optional[PickModes] = None,
            clear_buffer: Optional[bool] = None):
        '''
        Arguments
        ---------
        buffer_size:
            The size of the buffer.

        buffer_names:
            A list containing the names of buffer queues.

        pick_mode:
            The default mode to pick items from the list.

        clear_buffer:
            Whether to clear the buffer when `reset` is called.
        '''
        self._buffer: Union[None, Dict[str, Union[List[T1], List[T2]]]]
        self._buffer_size: Optional[int] = None
        self._buffer_names: Optional[List[str]] = None
        self._pick_mode: Optional[PickModes] = None
        self._clear_buffer: Optional[bool] = None
        self._buffer_index: int = -1
        self._count: int = 0

        self.setup(
            buffer_size=buffer_size, buffer_names=buffer_names,
            pick_mode=pick_mode, clear_buffer=clear_buffer)

    def setup(
            self, buffer_size: Optional[int] = None,
            buffer_names: Optional[List[str]] = None,
            pick_mode: Optional[PickModes] = None,
            clear_buffer: Optional[bool] = None) -> None:
        '''
        Set up the buffer.

        Arguments
        ---------
        buffer_size:
            The size of the buffer.

        buffer_names:
            A list containing the names of buffer elements.

        pick_mode:
            The default mode to pick items from the list.

        clear_buffer:
            Whether to clear the buffer when `reset` is called.

        Raises
        ------
        ValueError:
            Cannot modify `buffer_size`. The value is already set.

        ValueError:
            Cannot modify `buffer_names`. The value is already set.

        Notes
        -----
        `setup` should be used only for attributes of the buffer that are
        not defined. Attempt to use `setup` to modify size, names or mode will
        result in an exception.
        '''
        if buffer_size is not None:
            if self._buffer_size not in (None, buffer_size):
                raise ValueError(
                    'Cannot modify buffer_size. The value is already set.')
            else:
                self._buffer_size = buffer_size

        if buffer_names is not None:
            if self._buffer_names not in (None, buffer_names):
                raise ValueError(
                    'Cannot modify buffer_names. The value is already set.')
            else:
                self._buffer_names = buffer_names

        if self._buffer_size is not None and self._buffer_names is not None:
            self._buffer = {name: [None]*self._buffer_size  # type: ignore
                            for name in self._buffer_names}
        else:
            self._buffer = None

        if pick_mode is not None:
            self._pick_mode = pick_mode

        if clear_buffer is not None:
            self._clear_buffer = clear_buffer

        self.reset()

    def add(self, data: Dict[str, Union[T1, T2]]) -> None:
        '''
        Append a new item to the buffer.

        Arguments
        ---------
        data:
            A dictionary with the name of buffer queues as keys.

        Notes
        -----
        This implementation of `add` does not check if the buffer is full
        or if the provided names exist in the buffer queues. As a result, this
        situations will result in exceptions by the system.
        '''
        if self._buffer is None:
            raise RuntimeError('Buffer is not set up!')

        self._buffer_index += 1
        for key, v in data.items():
            self._buffer[key][self._buffer_index] = v  # type: ignore

        self._count += 1

    def pick(
            self,
            count: Optional[int] = None,
            mode: Optional[PickModes] = None
    ) -> Dict[str, Union[Tuple[T1, ...], Tuple[T2, ...]]]:
        '''
        Return items from the buffer.

        Arguments
        ---------
        count:
            The number of items to return. If omitted, the number of items in
            the buffer is used. `count` will be ignored if `mode` is 'all'.

        mode:
            How to pick items. If omitted, the default `pick_mode` specified
            during initialization or setup is used.

        Returns
        -------
        :
            A dictionary with buffer names as keys and picked items as values.

        Raises
        ------
        ValueError:
            The number of items requested is greater than the number of items
            in the buffer.

        ValueError:
            `mode` is not one of 'all', 'random', 'recent' and 'old'.
        '''
        _mode = mode.lower() if mode is not None else self._pick_mode
        _count = count if count is not None else self._count

        if _count > self._count:
            raise ValueError('Not enough data in the buffer.')

        if _mode == 'old':
            return self._pick_old(_count)
        elif _mode == 'recent':
            return self._pick_recent(_count)
        elif _mode == 'random':
            return self._pick_random(_count)
        elif _mode == 'all':
            return self._pick_all()
        else:
            raise ValueError(
                'mode should be one of all, old, recent, or random.')

    def aggregate(
        self, func: Union[
            Funcs, Callable[[Union[List[T1], List[T2]]], Union[T1, T2]]],
        names: Optional[Union[str, List[str]]] = None
    ) -> Dict[str, Union[T1, T2]]:
        if self._buffer is None:
            return {}

        _names: List[str]
        if names is None:
            _names = self._buffer_names  # type: ignore
        elif isinstance(names, str):
            _names = [names]
        else:
            _names = names

        if isinstance(func, str):
            if func == 'mean':
                fn = lambda x: sum(x) / len(x)
            elif func == 'sum':
                fn = sum
            elif func == 'min':
                fn = min
            elif func == 'max':
                fn = max
            elif func == 'count':
                fn = len
        else:
            fn = func

        return {
            name: fn(
                self._buffer[name][: self._buffer_index + 1])  # type: ignore
            for name in _names}

    def reset(self) -> None:
        '''
        Reset the buffer.
        '''
        if self._clear_buffer is not False:
            self._buffer_index = -1
            self._count = 0

    def _pick_old(
        self, count: int
    ) -> Dict[str, Union[Tuple[T1, ...], Tuple[T2, ...]]]:
        '''
        Return the oldest items in the buffer.

        Arguments
        ---------
        count:
            The number of items to return.

        Returns
        -------
        :
            A dictionary with buffer names as keys and `count` oldest items
            as values.
        '''
        if self._buffer:
            s = slice(count)
            return {name: tuple(buffer[s])  # type: ignore
                    for name, buffer in self._buffer.items()}
        else:
            raise RuntimeError('Buffer is not set up.')

    def _pick_recent(
        self, count: int
    ) -> Dict[str, Union[Tuple[T1, ...], Tuple[T2, ...]]]:
        '''
        Return the most recent items in the buffer.

        Arguments
        ---------
        count:
            The number of items to return.

        Returns
        -------
        :
            A dictionary with buffer names as keys and `count` most recent
            items as values.
        '''
        if self._buffer:
            s = slice(self._buffer_index - count + 1, self._buffer_index + 1)
            return {name: tuple(buffer[s])  # type: ignore
                    for name, buffer in self._buffer.items()}
        else:
            raise RuntimeError('Buffer is not set up.')

    def _pick_random(
        self, count: int
    ) -> Dict[str, Union[Tuple[T1, ...], Tuple[T2, ...]]]:
        '''
        Return a random sample of items in the buffer.

        Arguments
        ---------
        count:
            The number of items to return.

        Returns
        -------
        :
            A dictionary with buffer names as keys and `count` randomly picked
            items as values.
        '''
        if self._buffer:
            index = np.random.choice(  # type: ignore
                self._count, count, replace=False)
            return {name: tuple(buffer[i] for i in index)  # type: ignore
                    for name, buffer in self._buffer.items()}
        else:
            raise RuntimeError('Buffer is not set up.')

    def _pick_all(self) -> Dict[str, Union[Tuple[T1, ...], Tuple[T2, ...]]]:
        '''
        Return all items in the buffer.

        Returns
        -------
        :
            A dictionary with buffer names as keys and all items as values.
        '''
        if self._buffer:
            s = slice(self._buffer_index + 1)
            return {name: tuple(buffer[s])  # type: ignore
                    for name, buffer in self._buffer.items()}
        else:
            raise RuntimeError('Buffer is not set up.')

    def dump(self):
        pass
