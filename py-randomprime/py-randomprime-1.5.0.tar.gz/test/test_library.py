import unittest.mock

import py_randomprime


def test_patch_iso(tmp_path):
    py_randomprime.rust.patch_iso = unittest.mock.MagicMock()

    py_randomprime.patch_iso(
        tmp_path.joinpath("input.iso"),
        tmp_path.joinpath("output.iso"),
        {},
        py_randomprime.ProgressNotifier(print),
    )

    py_randomprime.rust.patch_iso.assert_called_once()
