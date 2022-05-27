#!/usr/bin/python3
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from .image import Image


class WindowBase(object, metaclass=ABCMeta):
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of the window.
        Returns None if no name is available.
        """

    @property
    @abstractmethod
    def pid(self) -> int:
        """
        Returns the process id of the window.
        Returns None if no pid is available.
        """

    @property
    @abstractmethod
    def active(self) -> bool:
        """
        Returns True if the window is active.
        Returns False if the window is not active.
        """

    @property
    @abstractmethod
    def geometry(self) -> tuple:
        """
        Returns: tuple: (x, y, width, height)
        """
        pass

    @abstractmethod
    def get_image(self, geometry: tuple = None) -> Image:
        """
        Returns an Image of the window.
        With the geometry parameter you can specify a sub-region of the window that will be captured.
        """

    @abstractmethod
    def send_chr(self, chr: chr) -> None:
        """
        send the keystroke of the given character to the window.
        """

    @abstractmethod
    def send_str(self, str: str) -> None:
        """
        Send keystrokes equivalent to the string you pass to the window.
        """

    @abstractmethod
    def warp_pointer(self, x: int, y: int, geometry: tuple = None) -> None:
        """
        Moves the pointer relative to the window to the given coordinates.
        """

    @abstractmethod
    def send_mouse_click(self, x: int, y: int, button) -> None:
        """
        Send a mouse click to the window at the given coordinates.
        On some windows/applications you need to move the pointer with warp_pointer() first.
        """

    def __repr__(self) -> str:
        name = self.name
        if name:
            name = f'"{name}"'
        return f'Window(name={name}, pid={self.pid}, active={self.active}, geometry={self.geometry})'
