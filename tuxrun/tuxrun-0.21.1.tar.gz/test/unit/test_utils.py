from tuxrun.utils import (
    ProgressIndicator,
    NoProgressIndicator,
    TTYProgressIndicator,
    notnone,
)


def test_progress_class(mocker):
    mocker.patch("sys.stderr.isatty", return_value=True)
    assert isinstance(ProgressIndicator.get("test"), TTYProgressIndicator)

    mocker.patch("sys.stderr.isatty", return_value=False)
    assert isinstance(ProgressIndicator.get("test"), NoProgressIndicator)


def test_notnone():
    assert notnone(None, "fallback") == "fallback"
    assert notnone("", "fallback") == ""
    assert notnone("hello", "fallback") == "hello"
