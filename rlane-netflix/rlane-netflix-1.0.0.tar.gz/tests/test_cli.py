from pathlib import Path

import pytest

from netflix.cli import main

ENCODING = "utf-8"
ROOT = Path("tests")
DIRS = {
    "input": ROOT / "input",
    "output": ROOT / "output",
    "expected": ROOT / "expected",
}


@pytest.mark.parametrize(
    ("basename"),
    [
        ("file1"),
    ],
)
def test_netflix(basename, monkeypatch, capsys):
    """Read input file, write output file, compare with expected file."""

    path_input = DIRS["input"].joinpath(basename).with_suffix(".csv")
    path_output = DIRS["output"].joinpath(basename).with_suffix(".txt")
    path_expected = DIRS["expected"].joinpath(basename).with_suffix(".txt")

    with open(path_input, encoding=ENCODING) as stdin:
        monkeypatch.setattr("sys.stdin", stdin)
        main(["-"])
        captured = capsys.readouterr()
        path_output.write_text(captured.out, encoding=ENCODING)
        expected = path_expected.read_text(encoding=ENCODING)
        assert captured.out == expected
