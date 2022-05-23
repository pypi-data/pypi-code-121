from dotpyle.objects.base import PathLike
from dotpyle.utils import path


class Script(object):
    """Script class to manage all relation with the capacity of Dotpyle to
    store, track and execute scripts"""

    __slots__ = ("_alias", "_filename")

    def __init__(self, alias: str, filename: str) -> None:
        """Initialize script object to be managed by Dotpyle"""
        self._alias = alias
        self._filename = filename

    @property
    def alias(self) -> str:
        return self._alias

    @alias.setter
    def alias(self, alias):
        self._alias = alias

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, filename):
        self._filename = filename

    def get_path(self) -> PathLike:
        """:return: filename full path"""
        return path.get_script_path(self._filename)

    def __str__(self) -> str:
        return "Script: {} located on {}".format(self._alias, self.get_path())

    def _serialize(self):
        return self._filename
        # return {self._alias: self._filename}
