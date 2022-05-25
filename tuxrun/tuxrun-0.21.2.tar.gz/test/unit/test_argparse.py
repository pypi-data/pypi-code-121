from argparse import Namespace, ArgumentTypeError
from pathlib import Path

import pytest

from tuxrun.argparse import filter_options, pathurlnone, pathnone, setup_parser


def test_filter_options():
    assert filter_options(Namespace()) == {}
    assert filter_options(Namespace(hello="world")) == {"hello": "world"}
    assert filter_options(Namespace(hello="world", debug=True)) == {"hello": "world"}


def test_pathurlnone():
    assert pathurlnone(None) is None
    assert pathurlnone("https://example.com/kernel") == "https://example.com/kernel"
    assert pathurlnone(__file__) == f"file://{Path(__file__).expanduser().resolve()}"

    with pytest.raises(ArgumentTypeError) as exc:
        pathurlnone("ftp://example.com/kernel")
    assert exc.match("Invalid scheme 'ftp'")

    with pytest.raises(ArgumentTypeError) as exc:
        pathurlnone("file:///should-not-exists")
    assert exc.match("/should-not-exists no such file or directory")


def test_pathnone():
    assert pathnone(None) is None
    assert pathnone(__file__) == Path(__file__).expanduser().resolve()

    with pytest.raises(ArgumentTypeError) as exc:
        pathnone("/should-not-exists")
    assert exc.match("/should-not-exists no such file or directory")


def test_timeouts_parser():
    assert setup_parser().parse_args(["--timeouts", "boot=1"]).timeouts == {"boot": 1}
    assert setup_parser().parse_args(
        ["--timeouts", "boot=1", "deploy=42"]
    ).timeouts == {"boot": 1, "deploy": 42}

    with pytest.raises(SystemExit):
        setup_parser().parse_args(["--timeouts", "boot=a"])

    with pytest.raises(SystemExit):
        setup_parser().parse_args(["--timeouts", "booting=1"])
