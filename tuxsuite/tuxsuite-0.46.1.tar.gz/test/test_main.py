# -*- coding: utf-8 -*-

import tuxsuite.__main__


def test_run(monkeypatch, mocker):
    run = tuxsuite.__main__.run
    main = mocker.patch("tuxsuite.__main__.main")
    monkeypatch.setattr(tuxsuite.__main__, "__name__", "__main__")
    run()
    main.assert_called()
