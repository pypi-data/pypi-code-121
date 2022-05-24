from saysynth.utils import bpm_to_time


def test_bpm_to_time_str_count():
    t = bpm_to_time(60, "1/16")
    assert t == 0.25


def test_bpm_to_str_count_time_sig():
    t = bpm_to_time(60, "1/8", "3/3")
    assert t == 0.375


def test_bpm_to_float_count():
    t = bpm_to_time(60, 1.0 / 8.0, "3/3")
    assert t == 0.375
