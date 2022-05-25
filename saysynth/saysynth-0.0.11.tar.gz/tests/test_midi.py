from saysynth.utils import here
from saysynth import midi


def test_valid_midi_file():
    messages = list(midi.process(here(__file__, "fixtures/valid.mid")))
    assert messages[0]["type"] == "note"
    assert messages[0]["note"] == 48
    assert messages[0]["velocity"] == 100
    assert messages[0]["duration"] == 4000.0
    assert messages[1]["type"] == "silence"
    assert messages[1]["duration"] == 500.0
    assert messages[-1]["type"] == "note"
    assert messages[-1]["note"] == 44
