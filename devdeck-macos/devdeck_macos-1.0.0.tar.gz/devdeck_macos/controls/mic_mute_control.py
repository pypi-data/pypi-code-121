import logging
import os

from osascript import osascript

from devdeck_core.controls.deck_control import DeckControl


class MicMuteControl(DeckControl):

    def __init__(self, key_no, **kwargs):
        self.muted = False
        super().__init__(key_no, **kwargs)

    def initialize(self):
        if self.__get_volume() == 0:
            self.muted = True
        self.__render_icon()

    def pressed(self):
        new_volume = 0
        if self.muted:
            new_volume = 100
        osascript(f"set volume input volume {new_volume}")
        self.muted = not self.muted
        self.__render_icon()

    def __get_volume(self):
        volume_query = osascript("input volume of (get volume settings)")
        return int(volume_query[1])

    def __render_icon(self):
        with self.deck_context() as context:
            if self.muted:
                with context.renderer() as r:
                    r.image(os.path.join(os.path.dirname(__file__), "../assets/font-awesome", 'microphone.png')).end()
            else:
                with context.renderer() as r:
                    r.image(os.path.join(os.path.dirname(__file__), "../assets/font-awesome", 'microphone-mute.png')).end()