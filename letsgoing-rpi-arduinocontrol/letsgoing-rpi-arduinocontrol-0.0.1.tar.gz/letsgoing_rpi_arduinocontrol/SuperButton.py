import os
from tkinter import Label
from PIL import ImageTk

from .resources import *

from math import floor

from .Config import config
from .Controller import controll

class SuperButton():
    
    def __init__(self, frame, index: int, pin) -> None:
        self.frame = frame
        self.pin = pin
        self.state = 0
        self.state_before = 0

        self.label = Label(self.frame)
        
        row = 2 * floor(index / config.buttons_per_row)
        column = int(index - (row/2) * config.buttons_per_row)
        self.label.grid(row=row,column=column, padx=2, pady=4, sticky="nsew")

        self.label.bind('<Button-1>', self.on_left_press)
        self.label.bind('<ButtonRelease-1>', self.on_left_release)
        self.label.bind('<Button-3>', self.on_right_press)
        self.label.bind('<ButtonRelease-3>', self.on_right_release)

    def set_mode(self, mode) -> None:
        self.mode = mode
        self.functionality = config.pin_modes[mode]

        imgOff = os.path.join(config.resource_path, self.mode + '-off.gif')
        imgOn = os.path.join(config.resource_path, self.mode + '-on.gif')
        self.imgOff = ImageTk.PhotoImage(file=imgOff)
        self.imgOn = ImageTk.PhotoImage(file=imgOn)
        self.label.config(image=self.imgOff)

        if self.functionality == "momentary_input" or self.functionality == "toggle_input":
            controll.unregister_input_listener(self)
        elif self.functionality == "digital_indicator":
            controll.register_input_listener(self)
        pass

    def input_listener(self, state: bool) -> None:
        if state != self.state:
            self.state = state
            if state:
                self.label.config(image=self.imgOn)
                self.label.image = self.imgOn
            else:
                self.label.config(image=self.imgOff)
                self.label.image = self.imgOff
        else:
            pass

    def on_left_press(self, Event) -> None:
        if self.functionality == "momentary_input" or "toggle_input":
            self.label.config(image=self.imgOn)
            self.state = 1
            controll.on_output_event(self.pin.internal, self.state)
        pass

    def on_left_release(self, Event) -> None:
        if self.functionality == "toggle_input":
            if self.state_before == self.state:
                self.state = 0
                self.label.config(image=self.imgOff)
            self.state_before = self.state
        elif self.functionality == "momentary_input":
            self.state = 0
            self.label.config(image=self.imgOff)
        if self.functionality == "momentary_input" or "toggle_input":
            controll.on_output_event(self.pin.internal, self.state)
        pass
    
    def on_right_press(self, Event) -> None:
        if self.functionality == "momentary_input" or "toggle_input":
            self.label.config(image=self.imgOn)
            self.state = 1
            controll.on_output_event(self.pin.internal, self.state)
        pass

    def on_right_release(self, Event) -> None:
        if self.functionality == "momentary_input":
            if self.state_before == self.state:
                self.state = 0
                self.label.config(image=self.imgOff)
            self.state_before = self.state
        elif self.functionality == "toggle_input":
            self.state = 0
            self.label.config(image=self.imgOff)
        if self.functionality == "momentary_input" or "toggle_input":
            controll.on_output_event(self.pin.internal, self.state)
        pass