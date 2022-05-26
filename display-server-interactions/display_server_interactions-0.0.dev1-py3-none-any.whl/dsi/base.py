#!/usr/bin/python3
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from .window import WindowBase


class DSIBase(object, metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def get_active_window() -> WindowBase:
        pass

    @staticmethod
    @abstractmethod
    def get_all_windows() -> list:
        """
        Returns: list: List of WindowBase objects.
        """
        pass

    @classmethod
    def get_window_by_pid(cls, pid: int) -> WindowBase:
        all_window = cls.get_all_windows()

        for window in all_window:
            if window.pid == pid:
                return window

    @classmethod
    def get_window_by_name(cls, name: str) -> WindowBase:
        all_window = cls.get_all_windows()

        for window in all_window:
            if window.name is not None and name in window.name:
                return window
