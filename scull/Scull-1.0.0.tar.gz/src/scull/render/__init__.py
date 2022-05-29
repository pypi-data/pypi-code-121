from abc import ABC, abstractmethod
from threading import Thread

class Renderer(ABC):
    def __init__(self, target):
        self.target = target
    
    @abstractmethod
    def render_lines(self, skeleton, options): pass
    @abstractmethod
    def clear_lines(self, skeleton): pass

    @abstractmethod
    def render_images(self, skeleton, options): pass
    @abstractmethod
    def clear_images(self, skeleton): pass
    
    def render(self, skeleton, options):
        self.clear_images(skeleton)
        self.render_images(skeleton, options)
