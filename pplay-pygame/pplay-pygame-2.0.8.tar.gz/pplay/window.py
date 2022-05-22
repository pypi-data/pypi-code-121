# coding= utf-8

# Pygame and system modules
import sys

import pygame
from pygame.locals import *

from pplay.exceptions import WindowNotInitialized
from pplay.keyboard import Keyboard
from pplay.mouse import Mouse
from pplay.sound import SoundMixer

# Initializes pygame's modules
pygame.init()

"""A simple Window class, it's the primary Surface(from pygame).
All the other game's renderable objects will be drawn on it. """


class Window:
    # A class attribute in Python, this case is similar to Java statics
    sound_mixer = None
    screen = None
    keyboard = None
    mouse = None

    """Initialize a Window (width x height)"""

    def __init__(self, width, height, sound_channels=8):
        # Controllers
        Window.sound_mixer = SoundMixer(sound_channels)
        Window.keyboard = Keyboard()
        Window.mouse = Mouse()

        # Fullscreen
        self.fullscreen = False
        self.fullscreen_width = pygame.display.Info().current_w
        self.fullscreen_height = pygame.display.Info().current_h
        self.windowed_width = width
        self.windowed_height = height

        # Size
        self.width = width
        self.height = height

        # Pattern color
        self.color = [0, 0, 0]  # Black

        # Pattern Title
        self.title = "Title"

        # Time Control
        self.curr_time = 0  # current frame time
        self.last_time = 0  # last frame time
        self.total_time = 0  # += curr-last(delta_time), update()

        # Creates the screen (pygame.Surface)
        # There are some useful flags (look pygame's docs)
        # It's like a static attribute in Java
        Window.screen = pygame.display.set_mode((self.width, self.height))
        # ? Why is it possible to do w.screen?

        # Sets pattern starting conditions
        self.set_background_color(self.color)
        self.set_title(self.title)

        # Updates the entire screen if no arguments are passed
        # Can be used to update portions of the screen (Rect list)
        pygame.display.update()

    def set_fullscreen(self):
        if self.fullscreen:
            return False

        self.fullscreen = True
        self.width = self.fullscreen_width
        self.height = self.fullscreen_height
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.FULLSCREEN
        )
        self.update()

        return True

    def set_windowed(self):
        if not self.fullscreen:
            return False

        self.fullscreen = False
        self.width = self.windowed_width
        self.height = self.windowed_height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.update()

        return True

    def set_resolution(self, width, height):
        self.windowed_width = width
        self.windowed_height = height

        if self.fullscreen:
            return

        self.width = self.windowed_width
        self.height = self.windowed_height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.update()

        return

    # -----------------------CONTROL METHODS---------------------------
    """Refreshes the Window - makes changes visible, AND updates the Time"""

    def update(self):
        pygame.display.update()  # refresh

        for event in pygame.event.get():  # necessary to not get errors
            if event.type == QUIT:
                self.close()
        self.last_time = self.curr_time  # set last frame time
        self.curr_time = pygame.time.get_ticks()  # since pygame.init()
        self.total_time += self.curr_time - self.last_time  # == curr_time
        # curr_time should be the REAL current time, but in Python
        # the method returns the time in seconds.
        # And we DO WANT MILLIseconds :P
        # While REAL time is not necessary, yet..

    """Paints the screen - White - and update"""

    def clear(self):
        self.set_background_color([255, 255, 255])
        self.update()

    # ---------------------GETTERS AND SETTERS METHODS-----------------
    """
    Changes background color - receives a vector [R, G, B] value
    Example: set_background_color([0,0,0]) -> black
    or set_background_color([255,255,255]) -> white
    """

    def set_background_color(self, rgb):
        self.color = rgb
        Window.screen.fill(self.color)

    # !Implement later possible strings values, such as:
    # "red","green","blue"..!

    """Gets the color attribute (background)"""

    def get_background_color(self):
        return self.color

    """Sets the title of the Window"""

    def set_title(self, title):
        self.title = title
        pygame.display.set_caption(title)

    """Gets the title of the Window"""

    def get_title(self):
        return self.title

    # ----------------------TIME CONTROL METHODS--------------------------

    """
    Returns the time passed between
    the last and the current frame - SECONDS
    """

    def delta_time(self):
        return (self.curr_time - self.last_time) / 1000.0

    """Returns the total time passed since the Window was created"""

    def time_elapsed(self):
        return self.total_time

    # ---------------------CLASS METHODS--------------------------
    """
    Closes the Window and stops the program - throws an exception
    """

    @classmethod
    def close(cls):
        pygame.quit()
        sys.exit()

    """Pause the program for an amount of time - milliseconds"""
    # Uses the processor to make delay accurate instead of
    # pygame.time.wait that SLEEPS the proccess
    @classmethod
    def delay(cls, time_ms):
        pygame.time.delay(time_ms)

    @classmethod
    def get_screen(cls):
        if cls.screen:
            return cls.screen

        raise WindowNotInitialized("screen")

    """Returns the keyboard input"""

    @classmethod
    def get_keyboard(cls):
        if cls.keyboard:
            return cls.keyboard

        raise WindowNotInitialized("keyboard")

    """Returns the mouse input"""

    @classmethod
    def get_mouse(cls):
        if cls.mouse:
            return cls.mouse

        raise WindowNotInitialized("mouse")
