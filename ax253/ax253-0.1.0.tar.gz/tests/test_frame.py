import pytest

from ax253 import Address, AX25BytestreamDecoder, Control, Frame


__author__ = "Masen Furer KF7HVM <kf7hvm@0x26.net>"
__copyright__ = "Copyright 2022 Masen Furer and Contributors"
__license__ = "Apache License, Version 2.0"


@pytest.mark.parametrize(
    "ax25_str, exp_frame",
    (
        (
            "FOO>APRS:!4605.21N/12327.31W#RNG0125Foo comment",
            Frame(
                destination=Address(
                    callsign=b"APRS", ssid=0, digi=False, a7_hldc=False
                ),
                source=Address(callsign=b"FOO", ssid=0, digi=False, a7_hldc=True),
                path=[],
                control=Control(b"\x03"),
                pid=b"\xf0",
                info=b"!4605.21N/12327.31W#RNG0125Foo comment",
            ),
        ),
    ),
)
def test_Frame_from_str(ax25_str, exp_frame):
    assert Frame.from_str(ax25_str) == exp_frame


@pytest.mark.parametrize(
    "chunks, exp_frames, exp_exception",
    (
        (
            [
                b"~\x82\xa0\xa4\xa6@@`\x9c`\x86\x82\x98\x98`\xae\x92\x88\x8ab@c\x03\xf0foo bar baz`\xa9~",
            ],
            [
                Frame(
                    destination=Address(
                        callsign=b"APRS",
                        ssid=0,
                        digi=False,
                        a7_hldc=False,
                    ),
                    source=Address(
                        callsign=b"N0CALL",
                        ssid=0,
                        digi=False,
                        a7_hldc=False,
                    ),
                    path=[Address(callsign=b"WIDE1", ssid=1, digi=False, a7_hldc=True)],
                    control=Control(b"\x03"),
                    pid=b"\xf0",
                    info=b"foo bar baz",
                ),
            ],
            None,
        ),
        (
            [
                b"~\x82\xa0\xa4\xa6@@`\x9c`\x86\x82\x98\x98`\xae\x92\x88\x8ab@c\x03\xf0foo bar baz",
            ],
            [
                Frame(
                    destination=Address(
                        callsign=b"APRS",
                        ssid=0,
                        digi=False,
                        a7_hldc=False,
                    ),
                    source=Address(
                        callsign=b"N0CALL",
                        ssid=0,
                        digi=False,
                        a7_hldc=False,
                    ),
                    path=[Address(callsign=b"WIDE1", ssid=1, digi=False, a7_hldc=True)],
                    control=Control(b"\x03"),
                    pid=b"\xf0",
                    info=b"foo bar baz",
                ),
            ],
            None,
        ),
        (
            [
                b"~\x82",
                b"\xa0\xa4\xa6",
                b"@@`\x9c",
                b"`\x86\x82",
                b"\x98\x98`\xae\x92\x88",
                b"\x8ab@c\x03",
                b"\xf0foo bar baz`",
                b"\xa9~",
            ],
            [
                Frame(
                    destination=Address(
                        callsign=b"APRS",
                        ssid=0,
                        digi=False,
                        a7_hldc=False,
                    ),
                    source=Address(
                        callsign=b"N0CALL",
                        ssid=0,
                        digi=False,
                        a7_hldc=False,
                    ),
                    path=[Address(callsign=b"WIDE1", ssid=1, digi=False, a7_hldc=True)],
                    control=Control(b"\x03"),
                    pid=b"\xf0",
                    info=b"foo bar baz",
                ),
            ],
            None,
        ),
        (
            [
                (
                    b"~\x82\xa0\xa4\xa6@@`\x9c`\x86\x82\x98\x98`\xae\x92\x88\x8ab@c\x03\xf0foo bar baz`\xa9~"
                    b"~\x82\xa0\xb4`lr`\x9c`\x86\x82\x98\x98`\xae\x92\x88\x8ab@b\x8c\x9e\x9e\x88\xa0@\xe1\x03\xf0digi'd 1\xcf\xcc~"
                )
            ],
            [
                Frame(
                    destination=Address(
                        callsign=b"APRS",
                        ssid=0,
                        digi=False,
                        a7_hldc=False,
                    ),
                    source=Address(
                        callsign=b"N0CALL",
                        ssid=0,
                        digi=False,
                        a7_hldc=False,
                    ),
                    path=[Address(callsign=b"WIDE1", ssid=1, digi=False, a7_hldc=True)],
                    control=Control(b"\x03"),
                    pid=b"\xf0",
                    info=b"foo bar baz",
                ),
                Frame(
                    destination=Address(
                        callsign=b"APZ069",
                        ssid=0,
                        digi=False,
                        a7_hldc=False,
                    ),
                    source=Address(
                        callsign=b"N0CALL",
                        ssid=0,
                        digi=False,
                        a7_hldc=False,
                    ),
                    path=[
                        Address(callsign=b"WIDE1", ssid=1, digi=False, a7_hldc=False),
                        Address(callsign=b"FOODP", ssid=0, digi=True, a7_hldc=True),
                    ],
                    control=Control(v=b"\x03"),
                    pid=b"\xf0",
                    info=b"digi'd 1",
                ),
            ],
            None,
        ),
        (
            [
                b"~\x82\xa0\xa4\xa6@@`\x9c`\x86\x82\x98\x98`\xae\x92\x88\x8ab@c\x03\xf0foo bar baz`\xa8~",
            ],
            [],
            "FCS did not match for",
        ),
    ),
    ids=["single frame", "truncated frame", "split frame", "2 frames", "bad fcs"],
)
def test_AX25BytestreamDecoder(chunks, exp_frames, exp_exception):
    decoded_frames = []
    d = AX25BytestreamDecoder()
    try:
        for c in chunks:
            decoded_frames.extend(d.update(c))
        decoded_frames.extend(d.flush())
    except Exception as exc:
        if exp_exception is None:
            raise
        assert exp_exception in str(exc)
    assert decoded_frames == exp_frames
