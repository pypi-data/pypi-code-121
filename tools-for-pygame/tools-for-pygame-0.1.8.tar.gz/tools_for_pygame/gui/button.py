#!/usr/bin/env python3

import time
from typing import Optional, Callable, Iterable, Any

import pygame.mixer

from .label import Label
from .gui_element import GUIElement
from tools_for_pygame.ani import AniBase
from tools_for_pygame.constants import BUTTON_NORMAL, BUTTON_CLICK, BUTTON_HOVER
from tools_for_pygame.element import MouseInteractionAniElement, Element


class Button(MouseInteractionAniElement, GUIElement):
    """
    Button(MouseInteractionAniElement)

    Type: class

    Description: a customizable button that can run a function
        when clicked

    Args:
        'normal_ani' (AniBase?): animation that plays when the button
            is idle
        'on_hover_ani' (AniBase?): animation that plays when the
            button is hovered by the cursor
        'on_click_ani' (AniBase?): animation that plays when the
            button is clicked
        'repeat_normal_ani' (bool): if the animation should be
            started each frame or only once
        'repeat_hover_ani' (bool): if the animation should be
            started each frame or only once
        'repeat_click_ani' (bool): if the animation should be
            started each frame or only once
        'text_label' (Label?): a Label that gets drawn in front of
            the button
        'hint_bg' (Element?): background of the hint shown when the
            mouse is hovering the button
        'hint_label' (Label?): text of the hint
        'hint_delay' (float): time in seconds to wait before showing
            the hint
        'func' (Callable): function to run when the button is pressed
        'func_args' (Iterable?): *args of the function
        'func_kwargs' (dict?): **kwargs of the function
        'func_as_method' (bool): makes the 'func' argument a method by
            adding the button object as the first positional argument
            of the function
        'button' (int): which mouse button should activate the button
            1 - left, 2 - middle, 3 - right
        'sound' (pygame.mixer.Sound?): a sound to play when the
            button is clicked

    Attrs:
        'normal_ani' (AniBase?): see 'normal_ani' in args
        'on_hover_ani' (AniBase?): see 'on_hover_ani' in args
        'on_click_ani' (AniBase?): see 'on_click_ani' in args
        'repeat_normal_ani' (bool): see 'repeat_normal_ani' in args
        'repeat_hover_ani' (bool): see 'repeat_hover_ani' in args
        'repeat_hover_ani' (bool): see 'repeat_hover_ani' in args
        'func' (Callable?): see 'func' in args
        'fargs' (Iterable?): see 'func_args' in args
        'fkwargs' (dict?): see 'func_kwargs' in args
        'func_as_method' (bool): see 'func_as_method' in args
        'button' (int): see 'button' in args
        'sound' (pygame.mixer.Sound?): see 'sound' in args
        'force_state' (int?): which state is shown of the button,
            if set to None the current one is shown.
            The module provides three constants BUTTON_NORMAL,
            BUTTON_HOVER and BUTTON_CLICK
        'label' (Label?): see 'label' in args
        'app' (Any): see 'app' in args

    Properties:
        'button_clicked' (bool, readonly): if the button is clicked
            with the assigned mouse button

    Methods:
        - run()
        - auto_run()
    """
    def __init__(self,
                 normal_ani: Optional[AniBase] = None,
                 on_hover_ani: Optional[AniBase] = None,
                 on_click_ani: Optional[AniBase] = None,
                 repeat_normal_ani: bool = False,
                 repeat_hover_ani: bool = False,
                 repeat_click_ani: bool = False,
                 text_label: Optional[Label] = None,
                 hint_bg: Optional[Element] = None,
                 hint_label: Optional[Label] = None,
                 hint_delay: float = 1,
                 func: Optional[Callable] = None,
                 func_args: Optional[Iterable] = None,
                 func_kwargs: Optional[dict] = None,
                 func_as_method: bool = False,
                 button: int = 0,
                 sound: Optional[pygame.mixer.Sound] = None,
                 app: Any = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        if normal_ani is not None:
            normal_ani.name = "normal_ani"
            normal_ani.id = -1
            self.add_ani(normal_ani)
        else: self.normal_ani = None

        if on_hover_ani is not None:
            on_hover_ani.name = "on_hover_ani"
            on_hover_ani.id = -1
            self.add_ani(on_hover_ani)
        else: self.on_hover_ani = None

        if on_click_ani is not None:
            on_click_ani.name = "on_click_ani"
            on_click_ani.id = -1
            self.add_ani(on_click_ani)
        else: self.on_click_ani = None

        self.repeat_normal_ani = repeat_normal_ani
        self.repeat_hover_ani = repeat_hover_ani
        self.repeat_click_ani = repeat_click_ani

        self.__started_ani = None

        self.func = func
        if func_args is None: func_args = []
        self.fargs = func_args
        if func_kwargs is None: func_kwargs = {}
        self.fkwargs = func_kwargs
        self.func_as_method = func_as_method

        self.button = button
        self.sound = sound

        self.__pressed = False
        self.force_state = None

        self.label = text_label
        if self.label: self.label.anchor(self)

        self.hint_bg = hint_bg
        self.hint_label = hint_label
        if self.hint_bg and self.hint_label:
            self.hint_label.anchor(self.hint_bg)
        self.start_hover = None
        self.hint_delay = hint_delay
        self.app = app

    @property
    def button_clicked(self):
        return self.clicked[self.button]

    def run(self) -> None:
        """Runs the button's function"""
        if not self.func:
            return
        if self.func_as_method:
            self.func(self, *self.fargs, **self.fkwargs)
        else:
            self.func(*self.fargs, **self.fkwargs)

    def auto_run(self) -> bool:
        """
        Calls 'run' automatically and plays the sound, should be called
        every frame
        """
        if self.button_clicked:
            if not self.__pressed and self.sound is not None:
                pygame.mixer.Sound.play(self.sound)
            self.__pressed = True
            return True
        elif self.hovered:
            if self.__pressed:
                self.run()
                self.__pressed = False
                return True
        else:
            self.__pressed = False

        return False

    def draw(self, *args, **kwargs) -> None:
        hovered = self.hovered
        clicked = self.button_clicked

        if self.force_state:
            if self.force_state == BUTTON_NORMAL:
                hovered = clicked = False
            elif self.force_state == BUTTON_HOVER:
                hovered = True
                clicked = False
            elif self.force_state == BUTTON_CLICK:
                clicked = True

        if clicked and self.on_click_ani is not None:
            if not self.__started_ani == "c" or self.repeat_click_ani:
                self.on_click_ani.start()
                self.__started_ani = "c"

        elif hovered and self.on_hover_ani is not None:
            if not self.__started_ani == "h" or self.repeat_hover_ani:
                self.on_hover_ani.start()
                self.__started_ani = "h"

        elif self.normal_ani is not None:
            if not self.__started_ani == "n" or self.repeat_normal_ani:
                self.normal_ani.start()
                self.__started_ani = "n"

        if self.hidden:
            self.start_hover = None
            return

        if self.hovered and self.start_hover is None:
            self.start_hover = time.perf_counter()
        elif not self.hovered or self.button_clicked:
            self.start_hover = None

        super().draw(*args, **kwargs)
        if self.label:
            self.label.draw(*args, **kwargs)

        if self.layout is None: return

        if self.hint_bg \
           and self.hint_label \
           and self.start_hover is not None \
           and time.perf_counter() - self.start_hover > self.hint_delay:
            self.layout._curr_button_hint = (
                id(self),
                self.hint_bg,
                self.hint_label
            )

        # Uses id to hide only its own hint
        elif self.layout._curr_button_hint is not None \
             and self.layout._curr_button_hint[0] == id(self):
            self.layout._curr_button_hint = None
