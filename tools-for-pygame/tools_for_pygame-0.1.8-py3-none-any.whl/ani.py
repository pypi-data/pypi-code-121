#!/usr/bin/env python3

"""
pgt.ani

Type: module

Description: module that contains the classes that define how animations
    work

Abstract classes:
    - FuncAniFrames
    - AniBase

Classes:
    - TextureAni
    - PosAni
    - TextAni

To make a custom animation you need to:

# make a class that inherits from pgt.AniBase
class MyAnimation(pgt.AniBase):

    # in the start method add a statement to save the initial value of
    # the attribute or property the animation changes

    # make sure to set it before calling super().start because this
    # method calls set_element()
    def start(self, *args, **kwargs):
        self.element_val = self.e.[ELEMENT_ATTRIBUTE]
        super().start(*args, **kwargs)

    def set_element(self):
        # here goes any operation that the animation should do when
        # it's running
        # you can use self.get_frame() to get the value of the current
        # frame, returned either by the function or the list of frames
        self.e.[ELEMENT_ATTRIBUTE] = self.get_frame()

    def reset_element(self):
        # here goes any operation that the animation should do when
        # the animation restores the initial value of the element
        self.e.[ELEMENT_ATTRIBUTE] = self.element_val


Here is the code of PosAni:

class PosAni(AniBase):
    def start(self, *args, **kwargs):
        # it copies the position into element_val
        self.element_val = self.e.pos.copy()
        super().start(*args, **kwargs)

    def set_element(self):
        # it assumes that get_frame() always returns a valid position
        self.e.pos = self.get_frame()

    def reset_element(self):
        # when the animation finishes, if reset_on_end is true, the
        # position saved is put back
        self.e.pos = self.element_val
"""
from __future__ import annotations

from abc import ABC as _ABC, abstractmethod as _abstractmethod
import time as _time
from typing import (Callable as _Callable,
                    Optional as _Optional,
                    Any as _Any,
                    Sequence as _Sequence,
                    Union as _Union)

from .element import AniElement
from .constants import (PERC as _PERC,
                        PREV_VAL as _PREV_VAL,
                        STARTING_VAL as _STARTING_VAL,
                        FRAME as _FRAME,
                        ANIMATION as _ANIMATION,
                        ELEMENT as _ELEMENT)


class FuncAniFrames:
    """
    FuncAniFrames

    Type: class

    Description: class used by subclasses of FuncAniBase to define
        frames that use a function and not a sequence

    Args:
        'function' (Callable): a function that returns a value that can
            later be used by the animation class
        'frames' (int): the total number of frames of the animation

    Attrs:
        '_func' (Callable): see 'function' in arguments
        '_frames' (int): see 'frames' in arguments

    Magic methods:
        '__len__()' (int): returns the total number of frames

    See tests/ani.PosAni.py for examples
    """
    def __init__(self, function: _Callable, frames: int):
        self._func = function
        self._frames = frames

    def __len__(self):
        return self._frames


class AniBase(_ABC):
    """
    AniBase(ABC)

    Type: abstract class

    Description: base to create an animation that can be used by
        an instance of pgt.element.AniElement or by a subclass

    Args:
        'name' (str): the name of the animation, it will be set as an
            attribute of the element that refers to this animation
        'element' (pgt.element.AniElement): the element to which the
            animation is assigned, defaults to None and should not be
            set manually, to set it use the pgt.element.AniElement.add_ani
            method to add the animation to an element
        'id_' (int): defaults to None, if set any animation running with
            the same id will be stopped upon calling the 'start' or
            'restart' methods
        'frames' (Sequence|FuncAniFrames): the frames of the animation
        'time' (float): the time that should elapse between frames
        'tot_time' (float): the time that should pass between the first
            and last frame, overwrites 'time' if set
        'loop' (bool): if the animation should restart after the last
            frame
        'reset_on_end' (bool): if at the end of the animation the
            starting value of the animation should be restored
        'starting_val' (Any): a value that specifies the starting point
            of the animation, is never changed
        'func_args' (int): what arguments should be passed to the
            function, these are:
            - PERC: the percentage of the animation (from 0 to 1)
            - PREV_VAL: the previous value returned by the function, if
                starting val is not set, the first time 'element_val' is
                passed
            - STARTING_VAL: 'start_val' in the arguments
            - FRAME: the number of the current frame
            - ANIMATION: the animation object itself
            - ELEMENT: the element that owns the animation
        'queue_ani' (AniBase?): the animation that starts when this one
            ends
        'max_updates_per_frame' (int): the maximum frames the animation
            can advance at once, 0 means no limit

    Attrs:
        'name' (str): see 'name' in arguments
        'id' (int): see 'id_' in arguments
        'frames' (iterable): see 'frames' in arguments
        'element_val' (Any): used to store the starting state of the
            animation to restore the original value
        'func_args' (int): see 'func_args' in arguments
        'starting_val' (Any): see 'starting_val' in arguments
        '_loop' (bool): see 'loop' in arguments
        '_current_frame' (int): the index of the frame currently
            displayed by the animation, if the animation was stopped
            or has ended, returns the index of the last shown frame
        '_last_frame' (float): the time that the last frame was shown
        '_ending' (bool): if the animation is going to stop before
            showing the next frame
        '_start_time' (float): when the animation started
        'e' (AniElement): the element of the animation
        '_reset_on_end' (bool): see 'reset_on_end' in arguments
        '_time' (float): see 'time' in arguments, if 'tot_time' is set
            '_time' will be automatically set
        '__using_func' (bool): if the animation is using a function or
            a list of frames predefined
        '__pending' (int): how many times the function should be called
            to keep up with the expected frame
        '__running': if the animation is currently playing
        '__prev_val' (Any): the previous value returned by the function
        '__tot_frames' (int): the total number of frames of the animation
        '__queued_ani' (AniBase?): see 'queued_ani' in args

    Methods:
        - start(starting_val, frame, start_time)
        - update(frame_time)
        - stop()
        - force_stop()
        - restart(*args, **kwargs)
        - get_frame()
        - set_frames(frames)
        - set_new_element(element)
        - set_queue_ani(ani)

    Magic methods:
        '__len__()' (int): returns the total duration of the animation in
            seconds

    Abstract methods:
        'set_element()' (None): changes the element according to the
            current frame (e.g. TextureAni changes the image)
        'reset_element()' (None): called only if 'reset_on_end' is true,
            resets the element to be like when the animation started
            (e.g. PosAni resets the element's position)
    """
    def __init__(self,
                 name: _Optional[str] = None,
                 element: _Optional[AniElement] = None,
                 id_: _Optional[int] = None,
                 frames: _Union[_Sequence, FuncAniFrames] = None,
                 time: float = 0.001,
                 tot_time: float = 0.0,
                 loop: bool = False,
                 reset_on_end: bool = True,
                 starting_val: _Any = None,
                 func_args: int = _PREV_VAL,
                 queued_ani: _Optional[AniBase] = None,
                 max_updates_per_frame: int = 0):

        if element is not None:
            setattr(element, name, self)

        self.e = element
        self.element_val = None
        self.id = id_
        self.frames = frames
        self.func_args = func_args
        self.name = name
        self.starting_val = starting_val
        self.max_updates = max_updates_per_frame

        self._current_frame = 0
        self._ending = False
        self._last_frame = 0
        self._loop = loop
        self._reset_on_end = reset_on_end
        self._start_time = 0
        self.__tot_frames = len(frames)

        self.__pending = 0
        self.__prev_val = starting_val
        self.__running = False
        self.__using_func = isinstance(self.frames, FuncAniFrames)
        self.__queued_ani = queued_ani

        if self.__queued_ani is not None and self.e is not None:
            self.__queued_ani.set_new_element(element)

        if tot_time != 0:
            self._time = tot_time / self.__tot_frames
        else:
            self._time = time

    def __repr__(self):
        return_string = f"name: {self.name}, frames: {self.__tot_frames}, "\
                        f"time: {self._time}, loop: {self._loop}"
        if self.id: return_string += f", id: {self.id}"
        return f"{self.__class__.__name__}({return_string})"

    @property
    def running(self):
        return self.__running

    def start(self,
              starting_val: _Any = None,
              frame: int = 0,
              start_time: _Optional[float] = None) -> None:
        """
        start(self, starting_val=None, frame=0, start_time=None)

        Type: method

        Description: starts the animation

        Args:
            'starting_val' (Any): the initial value of '__prev_val' when
                starting the animation
            'frame' (int): the frame the animation should be started at
            'start_time' (float): the time of the start of the animation,
                if None defaults to time.perf_counter()

        Return type: None
        """
        self.__prev_val = starting_val or self.starting_val

        if self._ending:
            self._ending = False
            return
        if self.__running:
            return
        if not start_time: start_time = _time.perf_counter()
        self._start_time = start_time
        self._last_frame = start_time
        self._current_frame = frame
        if self.id is None:
            self.e.current_ani.append((self.name, self.id))
        else:
            try:
                # overrides any animation with the same id
                ids = tuple(map(lambda x: x[1], self.e.current_ani))
                name = self.e.current_ani[ids.index(self.id)][0]
                getattr(self.e, name).force_stop()
                self.e.current_ani.append((self.name, self.id))
            except ValueError:
                self.e.current_ani.append((self.name, self.id))
        self.__running = True
        self.set_element()

    def update(self, frame_time: float, set_element: bool = True) -> None:
        """
        update(frame_time, set_element=True)

        Type: method

        Description: updates the animation and if necessary, changes
            frame(s)

        Args:
            'frame_time' (float): value that marks the current time for
                the animation, AniElement.update_ani() sets it to be
                the current time
            'set_element' (bool): if the set_element method should be
                called, defaults to True

        Return type: None
        """
        elapsed_time = frame_time - self._last_frame

        if elapsed_time < self._time: return

        if self._ending:
            self.force_stop()
            return

        try:
            new_frames = int(elapsed_time // self._time)
            if self.max_updates and new_frames > self.max_updates:
                new_frames = self.max_updates

            if self.__using_func:
                self.__pending = new_frames
            else:
                self._current_frame += new_frames
        except ZeroDivisionError:
            if self.__using_func:
                self.__pending += 1
            else:
                self._current_frame += 1

        if self.__using_func: self._current_frame += self.__pending

        if self._loop:
            if self._current_frame >= self.__tot_frames:
                self._start_time += self._time * self.__tot_frames
            self._current_frame %= self.__tot_frames
        elif self._current_frame >= self.__tot_frames:
            if self.__using_func:
                self.__pending -= self._current_frame % self.__tot_frames
                self._current_frame = self.__tot_frames
                self._ending = True
            else:
                self.force_stop()
                return

        self._last_frame = self._start_time + self._time * self._current_frame
        if set_element: self.set_element()

    def stop(self) -> None:
        """Stops the animation at the end of the current frame"""
        self._ending = True

    def force_stop(self) -> None:
        """Stops the animation instantly"""
        if not self.__running: return
        self._ending = False
        self.e.current_ani.remove((self.name, self.id))
        self.__running = False
        if self._reset_on_end:
            self.reset_element()
        if self.__queued_ani is not None:
            self.__queued_ani.start()

    def restart(self, *args, **kwargs) -> None:
        """
        restart(self, *args, **kwargs)

        Type: method

        Description: restarts the animation

        Args: if the animation ended, start is called and *args and
            **kwargs are passed as arguments

        Return type: None
        """
        if not self.__running:
            self.start(*args, **kwargs)
            return

        self._start_time = _time.perf_counter()
        self._last_frame = _time.perf_counter()
        self._current_frame = 0
        self._ending = False
        self.__running = True
        self.__pending = 0
        if self._reset_on_end:
            self.reset_element()

    def get_frame(self) -> _Any:
        """Returns the value of the current frame"""
        if not self.__using_func: return self.frames[self._current_frame]
        return_val = self.__prev_val
        if return_val is None and self.__pending == 0: return self.element_val
        for i in range(self.__pending):
            frame = self._current_frame - (self.__pending - i) + 1
            perc = frame / self.__tot_frames
            args = []
            if self.func_args & _PERC:         args.append(perc)
            if self.func_args & _PREV_VAL:     args.append(return_val)
            if self.func_args & _STARTING_VAL: args.append(self.starting_val)
            if self.func_args & _FRAME:        args.append(frame)
            if self.func_args & _ANIMATION:    args.append(self)
            if self.func_args & _ELEMENT:      args.append(self.e)
            return_val = self.frames._func(*args)
        self.__pending = 0
        self.__prev_val = return_val
        return return_val

    def set_frames(self, frames: _Union[_Sequence, FuncAniFrames]) -> None:
        """
        set_frames(self, frames)

        Type: method

        Description: changes the frames of the animation

        Args:
            'frames' (Sequence|FuncAniFrames): the new frames

        Return type: None
        """
        self.__tot_frames = len(frames)
        self.frames = frames
        self.__using_func = isinstance(self.frames, FuncAniFrames)

    def __len__(self):
        return self._time * self.__tot_frames

    def set_new_element(self, element):
        """Changes the element of the animation"""
        self.e = element
        if self.__queued_ani is not None:
            self.__queued_ani.set_new_element(element)
            self.__queued_ani.e.add_ani(self.__queued_ani)

    def set_queue_ani(self, ani: AniBase):
        """Changes the queued ani of the animation"""
        self.__queued_ani = ani
        self.__queued_ani.set_new_element(self.e)

    @_abstractmethod
    def set_element(self):
        pass

    @_abstractmethod
    def reset_element(self):
        pass


class TextureAni(AniBase):
    """
    TextureAni(AniBase)

    Type: class

    Description: animation that changes the texture of the element
    """
    def start(self, *args, **kwargs):
        self.element_val = self.e.image
        super().start(*args, **kwargs)

    def set_element(self):
        self.e.change_image(self.get_frame())

    def reset_element(self):
        self.e.image = self.element_val


class PosAni(AniBase):
    """
    TextureAni(FuncAniBase)

    Type: class

    Description: animation that changes the position of the element
    """
    def start(self, *args, **kwargs):
        self.element_val = self.e.pos.copy()
        super().start(*args, **kwargs)

    def set_element(self):
        self.e.pos = self.get_frame()

    def reset_element(self):
        self.e.pos = self.element_val


class TextAni(AniBase):
    """
    TextureAni(AniBase)

    Type: class

    Description: animation that changes the text of a label
    """
    def start(self, *args, **kwargs):
        self.element_val = self.e.text
        super().start(*args, **kwargs)

    def set_element(self):
        self.e.text = self.get_frame()

    def reset_element(self):
        self.e.text = self.element_val


class RotAni(AniBase):
    """
    TextureAni(FuncAniBase)

    Type: class

    Description: animation that changes the rotation of the element
    """
    def start(self, *args, **kwargs):
        self.element_val = self.e._rot
        super().start(*args, **kwargs)

    def set_element(self):
        self.e.rotate(self.get_frame(), True)

    def reset_element(self):
        self.e.rotate(self.element_val, True)


class ScaleAni(AniBase):
    """
    TextureAni(FuncAniBase)

    Type: class

    Description: animation that scales the element

    Args:
        'smooth' (bool): if the animation should use
        pygame.transform.smoothscale instead of pygame.transform.scale

    Attrs:
        'smooth': see 'smooth' in args
    """
    def __init__(self, smooth: bool = False, *args, **kwargs):
        self.smooth = smooth
        super().__init__(*args, **kwargs)

    def start(self, *args, **kwargs):
        self.element_val = self.e.size
        super().start(*args, **kwargs)

    def set_element(self):
        self.e.scale(self.get_frame(), self.smooth)

    def reset_element(self):
        self.e.scale(self.element_val)
