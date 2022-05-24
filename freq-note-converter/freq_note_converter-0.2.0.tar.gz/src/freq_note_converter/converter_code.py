import math
from dict_aligned_print import print_dict


class FreqNoteConverter:
    def __init__(self, freq=None, note_index=None, note=None, octave=None):
        self.note, self.octave, self.offset_from_note, self.note_index, self.offset_from_note = '', 0, 0, 0, 0
        if freq is not None:
            self.freq = freq
            self.note, self.octave, self.offset_from_note, self.note_index = self.freq_to_note(freq)
        elif note is not None and octave is not None:
            print('not implemented')
        elif note_index is not None:
            self.note_index = note_index
            self.note, self.octave, self.freq = self.note_index_to_freq(note_index)
        else:
            print('no valid input')

    def __str__(self):
        d = dict(freq=self.freq,
                 note_index=self.note_index,
                 note=self.note,
                 octave=self.octave,
                 offset_from_note=round(self.offset_from_note, 3))
        return print_dict(d, return_instead_of_print=True)
        # output = "\n".join(["{: >16} : {}".format(k, v) for k, v in d.items()])
        # output += '\n' + '-' * 50 + '\n'
        # return output

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def note_index_to_note_octave(note_index):
        notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

        note = (note_index - 1) % len(notes)
        note = notes[note]

        octave = (note_index + 8) // len(notes)

        return note, octave

    @staticmethod
    def freq_to_note_index(freq):
        if not freq:  # no log value for 0
            freq += 1e-15
        # formula taken from https://en.wikipedia.org/wiki/Piano_key_frequencies
        note_index = 12 * math.log2(freq / 440) + 49
        offset_from_note = note_index
        note_index = round(note_index)
        offset_from_note -= note_index
        return note_index, offset_from_note

    def freq_to_note(self, freq):
        note_index, offset_from_note = self.freq_to_note_index(freq)
        note, octave = self.note_index_to_note_octave(note_index)

        return note, octave, offset_from_note, note_index

    def note_index_to_freq(self, note_index):
        note, octave = self.note_index_to_note_octave(note_index)
        freq = 2 ** ((note_index - 49) / 12) * 440
        return note, octave, freq

    def print_me(self):
        print(self.__str__(), end='')
