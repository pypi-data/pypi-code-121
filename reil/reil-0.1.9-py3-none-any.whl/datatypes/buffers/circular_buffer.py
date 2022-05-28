# -*- coding: utf-8 -*-
'''
CircularBuffer class
====================

A `Buffer` that overflows!
'''

from typing import Callable, Dict, List, Optional, Tuple, Union

from reil.datatypes.buffers.buffer import Buffer, PickModes, T1, T2, Funcs


class CircularBuffer(Buffer[T1, T2]):
    '''
    A `Buffer` that overflows.

    Extends `Buffer` class.
    '''

    def __init__(
            self, buffer_size: Optional[int] = None,
            buffer_names: Optional[List[str]] = None,
            pick_mode: Optional[PickModes] = None) -> None:
        self._buffer_full: bool = False
        super().__init__(
            buffer_size=buffer_size, buffer_names=buffer_names,
            pick_mode=pick_mode)
        self._buffer_index = 0

    def add(self, data: Dict[str, Union[T1, T2]]) -> None:
        '''
        Add a new item to the buffer.

        Arguments
        ---------
        data:
            A dictionary with the name of buffer queues as keys.

        Notes
        -----
        If the buffer is full, new items will be writen over the oldest one.
        '''
        try:
            super().add(data)  # type: ignore
        except IndexError:
            self._buffer_full = True
            self._buffer_index = -1
            super().add(data)  # type: ignore

        # the size does not change if buffer is full.
        self._count -= self._buffer_full

    def aggregate(
            self, func: Union[Funcs, Callable[
                [Union[List[T1], List[T2]]],
                Union[T1, T2]]]) -> Dict[str, Union[T1, T2]]:
        if not self._buffer_full:
            return {}

        if isinstance(func, str):
            if func == 'mean':
                fn = lambda x: sum(x) / len(x)
            elif func == 'sum':
                fn = sum
            elif func == 'min':
                fn = min
            elif func == 'max':
                fn = max
        else:
            fn = func

        return {
            name: fn(values)  # type: ignore
            for name, values in self._buffer.items()}


    def _pick_old(
        self, count: int
    ) -> Dict[str, Union[Tuple[T1, ...], Tuple[T2, ...]]]:
        '''
        Return the oldest items in the buffer.

        Arguments
        ---------
        count:
            The number of items to return.
        '''
        if self._buffer_full:
            self._buffer_size: int
            slice_pre = slice(self._buffer_index + 1,
                              self._buffer_index + count + 1)
            slice_post = slice(
                max(0, count - (self._buffer_size - self._buffer_index) + 1))

            return {name: tuple(
                buffer[slice_pre] + buffer[slice_post])  # type: ignore
                for name, buffer in self._buffer.items()}
        else:  # filling starts from the first item, not 0th
            picks = super()._pick_old(count + 1)
            return {name: value[1:] for name, value in picks.items()}

    def _pick_recent(
        self, count: int
    ) -> Dict[str, Union[Tuple[T1, ...], Tuple[T2, ...]]]:
        '''
        Return the most recent items in the buffer.

        Arguments
        ---------
        count:
            The number of items to return.
        '''
        if count - self._buffer_index <= 1 or not self._buffer_full:
            return super()._pick_recent(count)
        elif self._buffer is not None:
            slice_pre = slice(-(count - self._buffer_index - 1), None)
            slice_post = slice(self._buffer_index + 1)
            return {name: tuple(
                buffer[slice_pre] + buffer[slice_post])  # type: ignore
                for name, buffer in self._buffer.items()}
        else:
            raise RuntimeError('Buffer is not set up.')

    def _pick_all(self) -> Dict[str, Union[Tuple[T1, ...], Tuple[T2, ...]]]:
        '''
        Return all items in the buffer.
        '''
        if self._buffer_full:
            self._buffer: Dict[str, Union[List[T1], List[T2]]]
            slice_pre = slice(self._buffer_index + 1, None)
            slice_post = slice(self._buffer_index + 1)
            return {name: tuple(
                buffer[slice_pre] + buffer[slice_post])  # type: ignore
                for name, buffer in self._buffer.items()}
        else:  # filling starts from the first item, not 0th
            picks = super()._pick_all()
            return {name: value[1:] for name, value in picks.items()}

    def reset(self) -> None:
        '''
        Reset the buffer.
        '''
        super().reset()
        self._buffer_index = 0
        self._buffer_full = False
