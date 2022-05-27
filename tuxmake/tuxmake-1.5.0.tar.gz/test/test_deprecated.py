from tuxmake import deprecated


class TestGetenv:
    def test_warning(self, monkeypatch, capsys):
        monkeypatch.setenv("FOO", "something")
        deprecated.getenv("FOO", "BAR")
        _, err = capsys.readouterr()
        assert "FOO is deprecated" in err
        assert "use BAR instead" in err
