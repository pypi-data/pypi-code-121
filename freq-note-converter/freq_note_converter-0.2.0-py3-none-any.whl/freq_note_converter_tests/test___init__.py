from unittest import TestCase
import random

import freq_note_converter


class Test(TestCase):
    def test_freq_from_freq(self):
        for _ in range(100):
            freq = random.randint(100, 1000)
            val = freq_note_converter.from_freq(freq)
            if val.freq != freq:
                self.fail(f'freq should be {freq} but module contains freq {val.freq}')

    def test_note_from_freq(self):
        frequencies = dict(A=440, B=493.9, C=523.3, D=587.3, E=659.3, F=698.5, G=784)
        for note, freq in frequencies.items():
            val = freq_note_converter.from_freq(freq)
            if val.note != note:
                self.fail(f'note should be {note} but module contains freq {val.note}')

    def test_from_note_index(self):
        frequencies = dict(A=49, B=51, C=52, D=54, E=56, F=57, G=59)
        for note, note_index in frequencies.items():
            val = freq_note_converter.from_note_index(note_index)
            if val.note != note:
                self.fail(f'note should be {note} but module contains freq {val.note}')
