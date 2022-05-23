import itertools
import pathlib
import stat
import tempfile

from fileperms import Permissions


class TestApply:
    def test(self):
        path = pathlib.Path(tempfile.mkstemp()[1])

        try:
            prm = Permissions()
            prm.apply(path)
            assert stat.filemode(path.lstat().st_mode)[1:] == prm.to_filemode()

            prm = Permissions.from_octal('777')
            prm.apply(path)
            assert stat.filemode(path.lstat().st_mode)[1:] == prm.to_filemode()
        finally:
            path.unlink()
