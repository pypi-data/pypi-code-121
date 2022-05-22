from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Optional
import tkinter as tk

# TODO: create abstract class and DotLevelMeter

from .signal_smoother import SignalSmoother


class LevelMeter(ABC):
    """Abstract class for level meters."""

    @abstractmethod
    def update_level(self, db: Optional[float]) -> None:
        """By convention, None is used to indicate no signal."""
        pass


class DotLevelMeter(LevelMeter):
    """Level meter that displays a colored dot."""

    class SignalLevel(IntEnum):
        white = -1
        grey = 0
        green = 1
        orange = 2
        red = 3

    def __init__(self, master, **kwargs):
        self._canvas = tk.Canvas(master=master, width=20, height=20)
        self._dot = self._canvas.create_oval(10, 10, 20, 20, fill='white')
        self._smoother = SignalSmoother(self.SignalLevel.white)
        self._canvas.grid(**kwargs)

    def _db_to_color(self, db: float) -> SignalLevel:
        if db < -10:
            return self.SignalLevel.grey
        if db < -4:
            return self.SignalLevel.green
        if db <= 0:
            return self.SignalLevel.orange
        return self.SignalLevel.red

    def update_level(self, db: Optional[float]) -> None:
        if db is None:
            self._smoother.reset()
            self._set_color(self.SignalLevel.white)
            return
        color = self._db_to_color(db)
        color = self._smoother(color)
        if color is None:
            return
        self._set_color(color)

    def _set_color(self, color: SignalLevel) -> None:
        self._canvas.itemconfigure(self._dot, fill=color.name)


class BarLevelMeter(LevelMeter):
    """
    A dB meter that shows the signal level as an array of 10 dots.

       grey                |  green  | orange  | red
    O....O....O....O....O....O....O....O....O....O
    -inf -21  -18  -15  -12  -9   -6   -3   0   saturation
    """
    class LED:
        def __init__(self, canvas, idx: int):
            self.canvas = canvas
            self.tag = canvas.create_oval(10 + 20 * idx, 10, 20 + 20 * idx, 20, fill='white')
            if idx < 5:
                self.color = 'grey'
            elif idx < 7:
                self.color = 'green'
            elif idx < 9:
                self.color = 'orange'
            else:
                self.color = 'red'

        def on(self):
            self.canvas.itemconfigure(self.tag, fill=self.color)

        def off(self):
            self.canvas.itemconfigure(self.tag, fill='white')

    def __init__(self, master, **kwargs):
        canvas = tk.Canvas(master=master, width=210, height=20)
        self.dots = [self.LED(canvas, i) for i in range(10)]
        self.prev_level = 0
        self._smoother = SignalSmoother(0)
        canvas.grid(**kwargs)

    @staticmethod
    def _db_to_level(db: float) -> int:
        """Convert a dB value to a level index between 1 and 10 (included)."""
        if db > 0:
            return 10
        # 0 and 10 are reserved values, hence the calculation may only return values between 1 and 9
        return max(1, min(9, int(round(db / 3 + 9))))

    def update_level(self, db: Optional[float]):
        if db is None:
            self.reset()
        level = self._smoother(self._db_to_level(db))
        if level is None:  # no change needed
            return
        if level > self.prev_level:
            for dot in range(self.prev_level, level):
                self.dots[dot].on()
        if level < self.prev_level:
            for dot in range(level, self.prev_level):
                self.dots[dot].off()
        self.prev_level = level

    def reset(self):
        for dot in range(0, self.prev_level):
            self.dots[dot].off()
        self.prev_level = 0
        self._smoother.reset()
