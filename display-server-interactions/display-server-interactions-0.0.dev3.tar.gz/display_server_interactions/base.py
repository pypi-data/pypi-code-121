#!/usr/bin/python3
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from .window import WindowBase
from platform import system


class DSIBase(object, metaclass=ABCMeta):
    @abstractmethod
    def get_active_window(self) -> WindowBase:
        """
        Gets the active window.
        Returns None if no window is active.
        """
        pass

    @abstractmethod
    def get_all_windows(self) -> list:
        """
        Returns a list of all Windows.
        """
        pass

    def get_window_by_pid(self, pid: int) -> WindowBase:
        """
        Get window by pid.
        Returns None if no window found.
        """
        all_window = self.get_all_windows()

        for window in all_window:
            if window.pid == pid:
                return window

    def get_window_by_name(self, name: str) -> WindowBase:
        """
        Get a window by name.
        Returns None if no window with that name is found.
        """
        all_window = self.get_all_windows()

        for window in all_window:
            if window.name is not None and name in window.name:
                return window

    @property
    def platform(self) -> str:
        """
        Returns the platform name.
        """
        return system().lower()

    @property
    def linux(self) -> bool:
        """
        Returns True if the platform is linux.
        """
        return self.platform == "linux"

    @property
    def windows(self) -> bool:
        """
        Returns True if the platform is windows.
        """
        return self.platform == "windows"

    @property
    def mac(self) -> bool:
        """
        Returns True if the platform is mac.
        """
        return self.platform == "darwin"

    # Allow dsi to be called with ’with’

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass
