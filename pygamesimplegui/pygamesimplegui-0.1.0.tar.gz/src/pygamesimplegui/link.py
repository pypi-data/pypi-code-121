import webbrowser
import pygame as pg

class Link:
    def __init__(
        self,
        text,
        link,
        center,
        font=pg.font.SysFont("verdana", 32),
        highlighted_font=pg.font.SysFont("verdana", 32),
        color="white",
        highlight_color="lightblue",
    ):
        self.text = text
        self.link = link
        self.center = center
        self.font = font
        self.highlighted_font = highlighted_font
        self.highlighted_font.set_underline(True)
        self.color = color
        self.highlight_color = highlight_color

        self.image = self.font.render(self.text, True, self.color)
        self.highlighted_image = self.highlighted_font.render(
            self.text, True, self.highlight_color
        )
        self.rect = self.image.get_rect(center=self.center)

        self.hovering = False
        self.pressed = False
        self.unpressed = False

    def draw(self, screen):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.hovering = True
            screen.blit(self.highlighted_image, self.rect.topleft)
            if any(pg.mouse.get_pressed()):
                self.pressed = True
                self.unpressed = False
            else:
                if self.pressed:
                    self.unpressed = True
                else:
                    self.unpressed = False
                self.pressed = False
        else:
            screen.blit(self.image, self.rect.topleft)
            if self.pressed:
                self.unpressed = True
            else:
                self.unpressed = False
            self.pressed = False
            self.hovering = False

    def update(self, screen):
        self.draw(screen)
        if self.unpressed:
            webbrowser.open(self.link)
