# -*- coding: utf-8 -*-
'''
Buffer class
============

The base class for all buffers in `reil`.
'''

from typing import Dict, List, Literal, Optional, Tuple, TypeVar, Union

from reil.datatypes.buffers.endless_buffer import EndlessBuffer, PickModes

T1 = TypeVar('T1')
T2 = TypeVar('T2')


class FillFlushBuffer(EndlessBuffer[T1, T2]):
    '''
    A buffer that returns only if it is full, and when any `pick` is called, it
    flushes the buffer.
    '''

    def __init__(
            self, buffer_names: Optional[List[str]] = None,
            buffer_size: Optional[int] = None,
            pick_mode: Optional[PickModes] = None) -> None:
        super(EndlessBuffer, self).__init__(
            buffer_size=buffer_size, buffer_names=buffer_names,
            pick_mode=pick_mode, clear_buffer=True)

    def setup(
            self, buffer_size: Optional[int] = None,
            buffer_names: Optional[List[str]] = None,
            pick_mode: Optional[PickModes] = None,
            clear_buffer: Optional[bool] = None) -> None:
        return super(EndlessBuffer, self).setup(
            buffer_size, buffer_names, pick_mode, clear_buffer)

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
        if self._buffer_index >= (self._buffer_size or 0) - 1:
            result = super().pick(count, mode)
            super().reset()
            # self._buffer = {
            #     name: [None]*self._buffer_size  # type: ignore
            #     for name in self._buffer_names}  # type: ignore
            # self._buffer_index = -1
            # self._count = 0
        elif self._buffer is None:
            result = {}
        else:
            result = {name: () for name in self._buffer}

        return result
