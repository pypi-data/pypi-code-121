import sys
import pygame as pg
pg.init()
from button import Button
from link import Link
from slider import Slider
from input_box import InputBox
from menu import Menu


class Window:
    def __init__(self):
        
        self.screen = pg.display.set_mode((1280, 720))
        self.center = self.screen.get_rect().center
        self.menu = Menu()
        self.menu.add_menu_item("Fourth thing")

        self.input_box = InputBox(center=self.center)

        self.link = Link("Open google", "www.google.com", center=(150, 600))

        self.r_slider = Slider(
            center=(180, 30),
            max=255,
            start_value=128,
            color="white",
            filled_color="red",
            show_value=True,
            show_label=True,
            label_text="R",
        )
        self.g_slider = Slider(
            center=(180, 60),
            max=255,
            start_value=128,
            color="white",
            filled_color="green",
            show_value=True,
            show_label=True,
            label_text="G",
        )
        self.b_slider = Slider(
            center=(180, 90),
            max=255,
            start_value=128,
            color="white",
            filled_color="blue",
            show_value=True,
            show_label=True,
            label_text="B",
        )
        self.r = 0
        self.g = 0
        self.b = 0

        self.reset_button = Button("Reset", (187, 150))

    def run(self):
        while True:
            self.screen.fill((self.r, self.g, self.b))
            self.handle_events(pg.event.get())

            self.menu.update(self.screen)
            self.input_box.update(self.screen)
            self.link.update(self.screen)

            pg.draw.rect(self.screen, "black", pg.Rect(5, 12, 375, 100), border_radius=5)
            pg.draw.rect(
                self.screen, "white", pg.Rect(5, 12, 375, 100), width=2, border_radius=5
            )

            self.r_slider.update(self.screen)
            self.g_slider.update(self.screen)
            self.b_slider.update(self.screen)

            self.r = self.r_slider.value
            self.g = self.g_slider.value
            self.b = self.b_slider.value

            self.reset_button.update(self.screen)

            if self.reset_button.unpressed:
                self.r_slider.reset()
                self.g_slider.reset()
                self.b_slider.reset()

            pg.display.update()

    def handle_events(self, events):
        if events:
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                self.menu.handle_event(event)
                self.input_box.handle_event(event)
        else:
            self.menu.handle_event(None)
            self.input_box.handle_event(None)


def main():
    window = Window()
    window.run()


if __name__ == "__main__":
    main()
