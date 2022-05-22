# coding= utf-8
from random import randint, seed
from typing import List

import pygame
import pygame.mixer

# Initizalizes pygame's modules
pygame.init()


class SoundMixer:
    channels: List[pygame.mixer.Channel] = []
    positions: List[int] = []

    def __init__(self, channels):
        seed(channels)
        pygame.mixer.set_num_channels(channels)
        pygame.mixer.init(channels=channels)

        SoundMixer.channels = [
            pygame.mixer.Channel(i) for i in range(channels)
        ]
        SoundMixer.positions = [0 for _ in range(channels)]

    @classmethod
    def play_sound(cls, sound_file, loop, rnd_code, know_position):
        kwargs = {"loops": -1} if loop else {}

        if know_position != -1:
            cls.positions[know_position] = rnd_code
            cls.channels[know_position].play(sound_file, **kwargs)
            return

        for position, channel in enumerate(cls.channels):
            if not channel.get_busy():
                channel.play(sound_file, **kwargs)
                cls.positions[position] = rnd_code

    @classmethod
    def stop_sound(cls, rnd_code, know_position):
        if know_position != -1:
            cls.positions[know_position] = 0
            cls.channels[know_position].stop()
            return

        for position, channel in enumerate(cls.channels):
            if cls.positions[position] == rnd_code:
                cls.positions[position] = 0
                channel.stop()

    @classmethod
    def is_plaing(cls, rnd_code, know_position):
        if know_position != -1:
            return cls.channels[know_position].get_busy()

        for position, channel in enumerate(cls.channels):
            if cls.positions[position] == rnd_code:
                return channel.get_busy()
        return False

    @classmethod
    def pause(cls, rnd_code, know_position):
        if know_position != -1:
            cls.channels[know_position].pause()
            return

        for position, channel in enumerate(cls.channels):
            if cls.positions[position] == rnd_code:
                channel.pause()

    @classmethod
    def unpause(cls, rnd_code, know_position):
        if know_position != -1:
            cls.channels[know_position].unpause()
            return

        for position, channel in enumerate(cls.channels):
            if cls.positions[position] == rnd_code:
                channel.unpause()

    @classmethod
    def fadeout(cls, rnd_code, time_ms, know_position):
        if know_position != -1:
            cls.channels[know_position].fadeout(time_ms)
            return

        for position, channel in enumerate(cls.channels):
            if cls.positions[position] == rnd_code:
                channel.fadeout(time_ms)

    @classmethod
    def set_volume(cls, rnd_code, value, know_position):
        value = 100 if value > 100 else value
        value = 0 if value < 0 else value
        float_value = float(value) * 0.01

        if know_position != -1:
            cls.channels[know_position].set_volume(float_value)
            return

        for position, channel in enumerate(cls.channels):
            if cls.positions[position] == rnd_code:
                channel.set_volume(float_value)


"""Sound é uma classe de controle dos sons do jogo - efeitos, música"""


class Sound:
    """ATENÇÃO! O arquivo passado deve ser .OGG!!! Se não pode gerar problemas."""

    def __init__(self, sound_file):
        self.loop = False
        self.sound = pygame.mixer.Sound(sound_file)
        self.volume = 50
        self.rnd_code = randint(9, 99999999)

    def set_volume(self, value, know_position=1):
        SoundMixer.set_volume(self.rnd_code, value, know_position)

    def increase_volume(self, value, know_position=-1):
        self.set_volume(self.volume + value, know_position)

    def decrease_volume(self, value, know_position=-1):
        self.set_volume(self.volume - value, know_position)

    def is_playing(self, know_position=-1):
        SoundMixer.is_plaing(self.rnd_code, know_position)

    def pause(self, know_position=-1):
        SoundMixer.pause(self.rnd_code, know_position)

    def unpause(self, know_position=-1):
        SoundMixer.unpause(self.rnd_code, know_position)

    def play(self, know_position=-1):
        SoundMixer.play_sound(
            self.sound, self.loop, self.rnd_code, know_position
        )

    def stop(self, know_position=-1):
        SoundMixer.stop_sound(self.rnd_code, know_position)

    def fadeout(self, time_ms, know_position=-1):
        SoundMixer.fadeout(self.rnd_code, time_ms, know_position)

    def set_repeat(self, repeat):
        self.loop = repeat
