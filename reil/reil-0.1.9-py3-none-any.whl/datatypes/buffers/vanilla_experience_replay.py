# -*- coding: utf-8 -*-
'''
VanillaExperienceReplay class
=============================

A `Buffer` with random pick that picks only if it is full.
'''

from typing import Dict, List, Optional, Tuple, Union

from reil.datatypes.buffers.circular_buffer import CircularBuffer
from reil.datatypes.buffers.buffer import T1, T2, PickModes


class VanillaExperienceReplay(CircularBuffer[T1, T2]):
    '''
    A `Buffer` with random pick that picks only if it is full.

    Extends `CircularBuffer` class.
    '''

    def __init__(
            self,
            buffer_size: Optional[int] = None,
            batch_size: Optional[int] = None,
            buffer_names: Optional[List[str]] = None,
            clear_buffer: bool = False) -> None:
        '''
        Initialize the buffer.

        Arguments
        -----------
        buffer_size:
            The size of the buffer.

        batch_size:
            The number of items to return at each `pick`.

        buffer_names:
            A list containing the names of buffer queues.

        clear_buffer:
            Whether to clear the buffer when `reset` is called.
        '''
        self._batch_size = None
        self._clear_buffer = False

        super().__init__(
            buffer_size=buffer_size,
            buffer_names=buffer_names, pick_mode='random')

        self.setup(
            buffer_size=buffer_size, batch_size=batch_size,
            buffer_names=buffer_names, clear_buffer=clear_buffer)

    def setup(
            self, buffer_size: Optional[int] = None,
            buffer_names: Optional[List[str]] = None,
            pick_mode: Optional[PickModes] = None,
            clear_buffer: Optional[bool] = None,
            batch_size: Optional[int] = None) -> None:
        '''
        Set up the buffer.

        Arguments
        ---------
        buffer_size:
            The size of the buffer.

        batch_size:
            The number of items to return at each `pick`.

        buffer_names:
            A list containing the names of buffer elements.

        clear_buffer:
            Whether to clear the buffer when `reset` is called.

        pick_mode:
            The default mode to pick items from the list. This argument is
            only available for signature consistency. Assigning it has
            no effect.

        Notes
        -----
        `setup` should be used only for attributes of the buffer that are
        not defined. Attempt to use `setup` to modify size, names or mode will
        result in an exception.
        '''
        super().setup(buffer_size=buffer_size,
                      buffer_names=buffer_names)

        if buffer_size is not None and buffer_size < 1:
            raise ValueError('buffer_size should be at least 1.')

        if self._buffer_size is not None:
            if batch_size is not None and self._buffer_size < batch_size:
                raise ValueError('buffer_size should be >= batch_size.')

        if batch_size is not None:
            if (self._buffer_size is not None and
                    self._buffer_size < batch_size):
                raise ValueError('buffer_size should be >= batch_size.')
            if self._batch_size not in (None, batch_size):
                raise ValueError(
                    'Cannot modify batch_size. The value is already set.')
            else:
                self._batch_size = batch_size

        self._clear_buffer = clear_buffer

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
            This argument is only available for signature consistency.
            Assigning it has no effect.

        mode:
            This argument is only available for signature consistency.
            Assigning it has no effect.

        Returns
        -------
        :
            `batch_size` number of items from the buffer randomly.
            If the buffer is not full, return empty tuples.

        '''
        if self._buffer_full:
            return super().pick(self._batch_size, 'random')
        else:
            return {name: () for name in self._buffer}  # type: ignore

    def reset(self) -> None:
        '''
        Reset the buffer if `clear_buffer` is set to `True`.
        '''
        if self._clear_buffer:
            super().reset()
            self._buffer_full = False
