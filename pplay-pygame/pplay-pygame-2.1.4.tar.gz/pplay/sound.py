# coding= utf-8
from random import randint, seed
from typing import List

import pygame
import pygame.mixer

# Initizalizes pygame's modules
pygame.init()


class SoundMixer:
    max_channels = 0
    positions: List[int] = []

    def __init__(self, channels):
        seed(channels)
        pygame.mixer.set_num_channels(channels)
        pygame.mixer.init(channels=channels)

        SoundMixer.max_channels = channels
        SoundMixer.positions = [0 for _ in range(channels)]

    @classmethod
    def set_volume(cls, rnd_code, value, know_position):
        value = 100 if value > 100 else value
        value = 0 if value < 0 else value
        float_value = float(value) * 0.01

        if know_position != -1:
            channel = pygame.mixer.Channel(know_position)
            channel.set_volume(float_value)
            return

        for i in range(cls.max_channels):
            if cls.positions[i] == rnd_code:
                channel = pygame.mixer.Channel(i)
                channel.set_volume(float_value)
                return

    @classmethod
    def play_sound(cls, sound, volume, loop, rnd_code, know_position):
        kwargs = {"loops": -1} if loop else {}

        if know_position != -1:
            channel = pygame.mixer.Channel(know_position)
            channel.play(sound, **kwargs)
            cls.set_volume(rnd_code, volume, know_position)
            cls.positions[know_position] = rnd_code
            return

        for i in range(cls.max_channels):
            if cls.positions[i] == rnd_code:
                channel = pygame.mixer.Channel(i)
                if not not channel.get_busy():
                    return

                channel.play(sound, **kwargs)
                cls.set_volume(rnd_code, volume, i)
                cls.positions[i] = rnd_code
                return

        for i in range(cls.max_channels):
            channel = pygame.mixer.Channel(i)
            if not channel.get_busy():
                channel.play(sound, **kwargs)
                cls.set_volume(rnd_code, volume, i)
                cls.positions[i] = rnd_code
                return

    @classmethod
    def stop_sound(cls, rnd_code, know_position):
        if know_position != -1:
            channel = pygame.mixer.Channel(know_position)
            channel.stop()
            cls.positions[know_position] = 0
            return

        for i in range(cls.max_channels):
            if cls.positions[i] == rnd_code:
                channel = pygame.mixer.Channel(i)
                channel.stop()
                cls.positions[i] = 0
                return

    @classmethod
    def is_plaing(cls, rnd_code, know_position):
        if know_position != -1:
            channel = pygame.mixer.Channel(know_position)
            return not not channel.get_busy()

        for i in range(cls.max_channels):
            if cls.positions[i] == rnd_code:
                channel = pygame.mixer.Channel(i)
                return not not channel.get_busy()
        return False

    @classmethod
    def pause(cls, rnd_code, know_position):
        if know_position != -1:
            channel = pygame.mixer.Channel(know_position)
            channel.pause()
            return

        for i in range(cls.max_channels):
            if cls.positions[i] == rnd_code:
                channel = pygame.mixer.Channel(i)
                channel.pause()
                return

    @classmethod
    def unpause(cls, rnd_code, know_position):
        if know_position != -1:
            channel = pygame.mixer.Channel(know_position)
            channel.unpause()
            return

        for i in range(cls.max_channels):
            if cls.positions[i] == rnd_code:
                channel = pygame.mixer.Channel(i)
                channel.unpause()
                return

    @classmethod
    def fadeout(cls, rnd_code, time_ms, know_position):
        if know_position != -1:
            channel = pygame.mixer.Channel(know_position)
            channel.fadeout(time_ms)
            return

        for i in range(cls.max_channels):
            if cls.positions[i] == rnd_code:
                channel = pygame.mixer.Channel(i)
                channel.fadeout(time_ms)
                return


"""Sound é uma classe de controle dos sons do jogo - efeitos, música"""


class Sound:
    """ATENÇÃO! O arquivo passado deve ser .OGG!!! Se não pode gerar problemas."""

    def __init__(self, sound_file):
        self.loop = False
        self.sound = pygame.mixer.Sound(sound_file)
        self.volume = 50
        self.rnd_code = randint(9, 99999999)

    def set_volume(self, value, know_position=1):
        self.volume = value
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
            self.sound, self.volume, self.loop, self.rnd_code, know_position
        )

    def stop(self, know_position=-1):
        SoundMixer.stop_sound(self.rnd_code, know_position)

    def fadeout(self, time_ms, know_position=-1):
        SoundMixer.fadeout(self.rnd_code, time_ms, know_position)

    def set_repeat(self, repeat):
        self.loop = repeat
