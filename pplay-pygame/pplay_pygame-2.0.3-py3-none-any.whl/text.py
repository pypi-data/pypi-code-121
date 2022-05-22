import pygame
from window import Window

# Initializes pygame's modules
pygame.init()


class Text:
    def __init__(
        self, x, y, text="", color=(255, 255, 255), size=64, font="Arial"
    ):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.textStr = str(text)

        self.font = pygame.font.SysFont(
            font, int(self.size * 0.7), bold=False, italic=False
        )
        self.text = self.font.render(self.textStr, True, self.color)
        self.text_rect = self.text.get_rect(center=(self.x, self.y))

    def draw(self):
        Window.screen.blit(self.text, self.text_rect)

    def update_position(self, x, y):
        self.__update(x=x, y=y)

    def update_color(self, color):
        self.__update(color=color)

    def update_size(self, size):
        self.__update(size=size)

    def update_text(self, text):
        self.__update(text=str(text))

    def __update(self, x=None, y=None, color=None, size=None, text=None):
        self.x = x or self.x
        self.y = y or self.y
        self.color = color or self.color
        self.size = size or self.size
        self.textStr = text or self.textStr

        self.text = pygame.font.Font(None, self.size).render(
            self.textStr, True, self.color
        )
        self.text_rect = self.text.get_rect(center=(self.x, self.y))
