"""Test decode CRLF delimited UI packets"""

from ax253 import Address, Frame, TNC2Decode

import pytest

idiotv = dict(
    frames=b"""
IDIOTV>BEACON,HEBOWX,N7QXO-9,qAR,KG7ZZA-10:T#890,174,193,087,046,080,00010011
IDIOTV>BEACON,HEBOWX,N7QXO-9,qAR,KG7ZZA-10:T#891,173,192,086,046,079,00010011
IDIOTV>APN391,HEBOWX,qAR,KG7ZZA-10:!4539.11NF12324.96W#PHG27651/KB7WUK OR Idiotville fill in
IDIOTV>BEACON,HEBOWX,N7QXO-9,qAR,KG7ZZA-10:T#892,172,191,088,046,079,00010011
IDIOTV>BEACON,HEBOWX,N7QXO-9,qAR,KG7ZZA-10:;145.270- T107.2 Timber OR see www.nwaprs.info for settings KB7WUK-11
IDIOTV>BEACON,HEBOWX,N7QXO-9,qAR,NPLNS:T#893,173,192,087,046,079,00010011
IDIOTV>BEACON,HEBOWX,N7QXO-9,qAR,SHERWD:T#894,173,191,088,047,079,00010011
IDIOTV>APN391,HEBOWX,qAR,NPLNS:!4539.11NF12324.96W#PHG27651/KB7WUK OR Idiotville fill in
    """,
    exp=[
        Frame(
            destination=Address(callsign=b"BEACON", ssid=0, digi=False, a7_hldc=False),
            source=Address(callsign=b"IDIOTV", ssid=0, digi=False, a7_hldc=False),
            path=[
                Address(callsign=b"HEBOWX", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"N7QXO", ssid=9, digi=False, a7_hldc=False),
                Address(callsign=b"QAR", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"KG7ZZA", ssid=10, digi=False, a7_hldc=True),
            ],
            control=b"\x03",
            pid=b"\xf0",
            info=b"T#890,174,193,087,046,080,00010011",
        ),
        Frame(
            destination=Address(callsign=b"BEACON", ssid=0, digi=False, a7_hldc=False),
            source=Address(callsign=b"IDIOTV", ssid=0, digi=False, a7_hldc=False),
            path=[
                Address(callsign=b"HEBOWX", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"N7QXO", ssid=9, digi=False, a7_hldc=False),
                Address(callsign=b"QAR", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"KG7ZZA", ssid=10, digi=False, a7_hldc=True),
            ],
            control=b"\x03",
            pid=b"\xf0",
            info=b"T#891,173,192,086,046,079,00010011",
        ),
        Frame(
            destination=Address(callsign=b"APN391", ssid=0, digi=False, a7_hldc=False),
            source=Address(callsign=b"IDIOTV", ssid=0, digi=False, a7_hldc=False),
            path=[
                Address(callsign=b"HEBOWX", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"QAR", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"KG7ZZA", ssid=10, digi=False, a7_hldc=True),
            ],
            control=b"\x03",
            pid=b"\xf0",
            info=b"!4539.11NF12324.96W#PHG27651/KB7WUK OR Idiotville fill in",
        ),
        Frame(
            destination=Address(callsign=b"BEACON", ssid=0, digi=False, a7_hldc=False),
            source=Address(callsign=b"IDIOTV", ssid=0, digi=False, a7_hldc=False),
            path=[
                Address(callsign=b"HEBOWX", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"N7QXO", ssid=9, digi=False, a7_hldc=False),
                Address(callsign=b"QAR", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"KG7ZZA", ssid=10, digi=False, a7_hldc=True),
            ],
            control=b"\x03",
            pid=b"\xf0",
            info=b"T#892,172,191,088,046,079,00010011",
        ),
        Frame(
            destination=Address(callsign=b"BEACON", ssid=0, digi=False, a7_hldc=False),
            source=Address(callsign=b"IDIOTV", ssid=0, digi=False, a7_hldc=False),
            path=[
                Address(callsign=b"HEBOWX", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"N7QXO", ssid=9, digi=False, a7_hldc=False),
                Address(callsign=b"QAR", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"KG7ZZA", ssid=10, digi=False, a7_hldc=True),
            ],
            control=b"\x03",
            pid=b"\xf0",
            info=b";145.270- T107.2 Timber OR see www.nwaprs.info for settings KB7WUK-11",
        ),
        Frame(
            destination=Address(callsign=b"BEACON", ssid=0, digi=False, a7_hldc=False),
            source=Address(callsign=b"IDIOTV", ssid=0, digi=False, a7_hldc=False),
            path=[
                Address(callsign=b"HEBOWX", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"N7QXO", ssid=9, digi=False, a7_hldc=False),
                Address(callsign=b"QAR", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"NPLNS", ssid=0, digi=False, a7_hldc=True),
            ],
            control=b"\x03",
            pid=b"\xf0",
            info=b"T#893,173,192,087,046,079,00010011",
        ),
        Frame(
            destination=Address(callsign=b"BEACON", ssid=0, digi=False, a7_hldc=False),
            source=Address(callsign=b"IDIOTV", ssid=0, digi=False, a7_hldc=False),
            path=[
                Address(callsign=b"HEBOWX", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"N7QXO", ssid=9, digi=False, a7_hldc=False),
                Address(callsign=b"QAR", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"SHERWD", ssid=0, digi=False, a7_hldc=True),
            ],
            control=b"\x03",
            pid=b"\xf0",
            info=b"T#894,173,191,088,047,079,00010011",
        ),
        Frame(
            destination=Address(callsign=b"APN391", ssid=0, digi=False, a7_hldc=False),
            source=Address(callsign=b"IDIOTV", ssid=0, digi=False, a7_hldc=False),
            path=[
                Address(callsign=b"HEBOWX", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"QAR", ssid=0, digi=False, a7_hldc=False),
                Address(callsign=b"NPLNS", ssid=0, digi=False, a7_hldc=True),
            ],
            control=b"\x03",
            pid=b"\xf0",
            info=b"!4539.11NF12324.96W#PHG27651/KB7WUK OR Idiotville fill in",
        ),
    ],
)


@pytest.mark.parametrize(
    "packet_data,exp_frames,exp_exception",
    (
        (
            idiotv["frames"],
            idiotv["exp"],
            None,
        ),
    ),
)
def test_tnc2_decode(packet_data, exp_frames, exp_exception):
    try:
        assert list(TNC2Decode().update(packet_data)) == exp_frames
    except Exception as exc:
        if exp_exception:
            assert exp_exception in str(exc)
        raise
