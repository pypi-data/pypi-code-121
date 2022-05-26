import pygame as pg


class Button:
    def __init__(
        self,
        text: str,
        center: tuple[int, int],
        font: pg.font.Font = pg.font.SysFont("verdana", 32),
        color="lightgray",
        hover_background="black",
    ) -> None:
        """Initialize a new button

        Args:
            text : Text to show on button.
            center : Coordinates of center of the button. Defaults to center of screen).
            font : Font for the text on the button. Defaults to pg.font.SysFont("verdana", 32).
            color : Color of the text on the button. Defaults to light gray.
        """
        self.text = text
        self.font = font
        self.image = self.font.render(self.text, True, color)
        self.image_rect = self.image.get_rect(center=center)
        self.rect = self.image.get_rect(center=center).inflate(25, 25)
        self.rect_surf = pg.Surface((self.rect.w, self.rect.h))
        self.rect_surf.fill(hover_background)
        self.rect_surf.set_alpha(100)
        self.hovering = False
        self.pressed = False
        self.unpressed = False

    def hover(self, screen) -> None:
        """Handles the mouse hovering over the button"""
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.hovering = True
            self.unpressed = False
            screen.blit(self.rect_surf, self.rect.topleft)
            if any(pg.mouse.get_pressed()):
                self.pressed = True
            else:
                if self.pressed:
                    self.unpressed = True
                self.pressed = False
        else:
            self.hovering = False
            self.pressed = False
            self.unpressed = False

    def draw(self, screen) -> None:
        """Draws the text of the button"""
        screen.blit(self.image, self.image_rect.topleft)

    def update(self, screen) -> None:
        """Update the button"""
        self.hover(screen)
        self.draw(screen)
