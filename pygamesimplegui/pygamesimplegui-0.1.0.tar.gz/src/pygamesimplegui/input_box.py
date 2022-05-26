import pygame as pg


class InputBox:
    def __init__(
        self,
        center,
        width=200,
        height=50,
        text="",
        font=pg.font.SysFont("verdana", 20),
        inactive_color="lightskyblue3",
        active_color="dodgerblue2",
        cursor_color="white",
    ):
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.image = pg.Surface((width, height))
        self.rect = self.image.get_rect(center=center)
        self.text = text
        self.font = font
        self.color = self.inactive_color
        self.text_image = self.font.render(text, True, self.color)
        self.text_rect = self.text_image.get_rect(
            midleft=(self.rect.left + 5, self.rect.centery)
        )
        self.active = False
        self.pressed = False
        self.counter = 0
        self.cursor_image = pg.Surface((1, 30))
        self.cursor_image.fill(cursor_color)
        self.cursor_rect = self.cursor_image.get_rect(center=self.text_rect.midright)

    def handle_event(self, event):
        if event is not None and event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pg.mouse.get_pos()):
                self.active = not self.active

            else:
                self.active = False

        self.color = self.active_color if self.active else self.inactive_color
        if self.active:
            if event is not None:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        self.text = ""
                    elif event.key == pg.K_BACKSPACE:
                        self.text = self.text[:-1]
                        self.pressed = True
                    else:
                        self.text += event.unicode
                if event.type == pg.KEYUP:
                    self.pressed = False
            # if self.pressed:
            #     self.counter += 1
            # else:
            #     self.counter = 0

            self.counter = self.counter + 1 if self.pressed else 0

            if self.counter > 100:
                self.text = self.text[:-1]
                self.counter = 80

            self.text_image = self.font.render(self.text, True, self.color)
            self.text_rect = self.text_image.get_rect(topleft=self.text_rect.topleft)
            self.cursor_rect = self.cursor_image.get_rect(
                center=self.text_rect.midright
            )

    def draw(self, screen):
        screen.blit(self.text_image, self.text_rect.topleft)
        pg.draw.rect(screen, self.color, self.rect, width=2, border_radius=5)
        if self.active:
            screen.blit(self.cursor_image, self.cursor_rect.topleft)

    def update(self, screen):
        self.draw(screen)
