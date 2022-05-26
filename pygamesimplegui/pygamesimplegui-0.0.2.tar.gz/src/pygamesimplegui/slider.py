from .settings import *


class Slider:

    busy = False

    def __init__(
        self,
        center=(WIDTH / 2, HEIGHT / 2),
        min=0,
        max=100,
        start_value=None,
        width=250,
        height=5,
        color=(255, 255, 255),
        filled_color=(0, 128, 128),
        show_value=False,
        show_label=False,
        label_text: str = "Placeholder",
        font=pg.font.SysFont("verdana", 16),
        font_color=(255, 255, 255),
    ) -> None:
        self.width = width
        self.height = height
        self.color = color
        self.filled_color = filled_color
        self.image = pg.Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=center)
        self.max = max
        self.min = min
        self.range = self.max - self.min

        self.start_value = start_value
        if self.start_value is None:
            self.start_value = self.min
        self.value = self.start_value

        self.filled_image = pg.Surface(
            ((self.value - self.min) * self.width / self.range, self.height)
        )
        self.filled_image.fill(self.filled_color)
        self.filled_rect = self.filled_image.get_rect(topleft=self.rect.topleft)
        self.pressed = False

        self.show_value = show_value
        self.show_label = show_label

        if self.show_label or self.show_value:
            self.font = font
            self.font_color = font_color

        if self.show_value:
            self.value_image = self.font.render(
                f"{round(self.value)}", True, self.font_color
            )
            self.value_rect = self.value_image.get_rect(
                midleft=(self.rect.right + 20, self.rect.centery)
            )

        if self.show_label:
            self.label_text = label_text
            self.label_image = self.font.render(self.label_text, True, self.font_color)
            self.label_rect = self.label_image.get_rect(
                midright=(self.rect.left - 20, self.rect.centery)
            )

    def draw(self):
        screen.blit(self.image, self.rect.topleft)
        screen.blit(self.filled_image, self.filled_rect.topleft)
        pg.draw.circle(
            screen,
            self.filled_color,
            (
                self.rect.left + (self.value - self.min) / self.range * self.width,
                self.rect.centery,
            ),
            8,
        )
        if self.show_value:
            screen.blit(self.value_image, self.value_rect.topleft)
        if self.show_label:
            screen.blit(self.label_image, self.label_rect.topleft)

    def update_value(self):
        x, y = pg.mouse.get_pos()
        if any(pg.mouse.get_pressed()):
            if self.rect.collidepoint(x, y) and not Slider.busy:
                Slider.busy = True
                self.pressed = True
            if self.pressed:
                self.value = (x - self.rect.left) * self.range / self.width + self.min
                if x > self.rect.right:
                    self.value = self.max
                elif x < self.rect.left:
                    self.value = self.min

            self.set_value()

        else:
            self.pressed = False
            Slider.busy = False

    def update(self):
        self.update_value()
        self.draw()

    def set_value(self, value=None):
        if value is not None:
            self.value = value
        self.filled_image = pg.Surface(
            ((self.value - self.min) * self.width / self.range, self.height)
        )
        self.filled_image.fill(self.filled_color)
        self.filled_rect = self.filled_image.get_rect(topleft=self.rect.topleft)
        if self.show_value:
            self.value_image = self.font.render(
                f"{round(self.value)}", True, self.font_color
            )
            self.value_rect = self.value_image.get_rect(
                midleft=(self.rect.right + 20, self.rect.centery)
            )

    def reset(self):
        self.set_value(self.start_value)
