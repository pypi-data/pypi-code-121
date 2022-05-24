# -*- coding: utf-8 -*-

from tuxsuite.cli.utils import datediff


def test_datediff():
    one = "2021-10-28T06:16:48"
    two = "2021-10-27T13:46:09"
    res = datediff(None, two)
    assert res == two
    res = datediff(one, one)
    assert res == "\x1b[37m2021-10-28T06:16:48\x1b[0m"
    res = datediff(one, two)
    assert res == "\x1b[37m2021-10-2\x1b[0m7T13:46:09"
