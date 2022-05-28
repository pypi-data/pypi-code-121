# -*- coding: utf-8 -*-
'''
EndlessBuffer class
===================

A `Buffer` without size limit.
'''

from typing import Dict, List, Optional, Union

from reil.datatypes.buffers.buffer import Buffer, PickModes, T1, T2


class EndlessBuffer(Buffer[T1, T2]):
    '''
    A `Buffer` without size limit.

    Extends `Buffer` class.
    '''

    def __init__(
            self,
            buffer_names: Optional[List[str]] = None,
            pick_mode: Optional[PickModes] = None) -> None:
        '''
        Arguments
        ---------
        buffer_names:
            A list containing the names of buffer queues.

        pick_mode:
            The default mode to pick items from the list.
        '''
        self.setup(buffer_names=buffer_names, pick_mode=pick_mode)

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
            The size of the buffer. This argument is only available for
            signature consistency. Assigning it has no effect.

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
        super().setup(
            buffer_names=buffer_names, pick_mode=pick_mode,
            clear_buffer=clear_buffer)

    def add(self, data: Dict[str, Union[T1, T2]]) -> None:
        '''
        Add a new item to the buffer.

        Arguments
        ---------
        data:
            A dictionary with the name of buffer queues as keys.
        '''
        if self._buffer is not None:
            self._buffer_index += 1
            for key, v in data.items():
                self._buffer[key].append(v)  # type: ignore
            self._count += 1

        else:
            raise RuntimeError('Buffer is not set up.')

    def reset(self) -> None:
        '''
        Reset the buffer.
        '''
        super().reset()
        if self._buffer_names is not None:
            self._buffer = {name: []  # type: ignore
                            for name in self._buffer_names}
        else:
            self._buffer = None  # type: ignore
