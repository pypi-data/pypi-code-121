#!/usr/bin/python3
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from .image import Image


class WindowBase(object, metaclass=ABCMeta):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def pid(self) -> int:
        pass

    @property
    @abstractmethod
    def active(self) -> bool:
        pass

    @property
    @abstractmethod
    def geometry(self) -> tuple:
        """
        Returns: tuple: (x, y, width, height)
        """
        pass

    @abstractmethod
    def get_image(self, geometry: tuple = None) -> Image:
        pass

    @abstractmethod
    def send_chr(self, chr: chr) -> None:
        pass

    @abstractmethod
    def send_str(self, str: str) -> None:
        pass

    @abstractmethod
    def warp_pointer(self, x: int, y: int, geometry: tuple = None) -> None:
        pass

    @abstractmethod
    def send_mouse_click(self, x: int, y: int, button) -> None:
        pass
