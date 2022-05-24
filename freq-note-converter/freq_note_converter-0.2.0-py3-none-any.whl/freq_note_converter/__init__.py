"""
convert frequency to note and note to frequency.
currently, can only input frequency and note index, and not supporting note name and octave as input


usage example:
    input:
        import freq_note_converter

        val = freq_note_converter.from_freq(449)
        print(val.note)
    output:
        'A'
    input:
        print(val)
    output:
                    freq : 449
             note_index : 49
                    note : A
                  octave : 4
        offset_from_note : 0.351
        --------------------------------------------------
    input:
        freq_note_converter.from_note_index(49).print_me()
    output:
                    freq : 440.0
             note_index : 49
                    note : A
                  octave : 4
        offset_from_note : 0
        --------------------------------------------------
"""
from freq_note_converter import converter_code


def from_freq(freq):
    return _convert(freq=freq)


def from_note_index(note_index):
    return _convert(note_index=note_index)


def _convert(freq=None, note_index=None):
    if freq is not None:
        converter = converter_code.FreqNoteConverter(freq=freq)
    elif note_index is not None:
        converter = converter_code.FreqNoteConverter(note_index=note_index)
    else:
        print('no valid input')
    return converter
