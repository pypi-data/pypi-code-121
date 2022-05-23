import unittest
from dataclasses import dataclass
from typing import Dict, List, Optional
from unittest.mock import patch

from honesty.cache import Cache

from honesty.version import Version
from packaging.requirements import Requirement

from pessimist.manager import _filter_versions, Manager


@dataclass
class FileEntry:
    requires_python: Optional[str]


@dataclass
class FakeRelease:
    files: List[FileEntry]


@dataclass
class FakePackage:
    releases: Dict[Version, FakeRelease]


class ManagerTest(unittest.TestCase):
    def test_is_pip_line(self) -> None:
        self.assertTrue(Manager._is_pip_line("-e ../"))
        self.assertTrue(Manager._is_pip_line("-r r.txt"))
        self.assertTrue(Manager._is_pip_line("../"))
        self.assertTrue(Manager._is_pip_line("git+https://example.com/"))
        self.assertFalse(Manager._is_pip_line("pessimist"))
        self.assertFalse(Manager._is_pip_line("pessimist>=1.0"))

    def test_filter_versions(self) -> None:
        python_version = Version("3.7.0")
        pkg = FakePackage(
            releases={
                Version("1.0"): FakeRelease([FileEntry(">=2.7")]),
                Version("2.0"): FakeRelease([FileEntry(None)]),
                Version("2.1"): FakeRelease([FileEntry(">=3.8")]),
            }
        )

        c = Cache()

        with patch("pessimist.manager.parse_index", lambda *args, **kwargs: pkg):
            _, versions = _filter_versions(
                req=Requirement("p"), cache=c, python_version=python_version
            )
            self.assertEqual([Version("1.0"), Version("2.0")], versions)

            _, versions = _filter_versions(
                req=Requirement("p>=2.0"), cache=c, python_version=python_version
            )
            self.assertEqual([Version("2.0")], versions)

            # extend doesn't match, doesn't change
            _, versions = _filter_versions(
                req=Requirement("p>=2.0"),
                cache=c,
                python_version=python_version,
                extend=["foo"],
            )
            self.assertEqual([Version("2.0")], versions)

            # does match; still obeys requires_python because pip will
            _, versions = _filter_versions(
                req=Requirement("p>=2.0"),
                cache=c,
                python_version=python_version,
                extend=["p"],
            )
            self.assertEqual([Version("1.0"), Version("2.0")], versions)

            # does match; still obeys requires_python because pip will (*)
            _, versions = _filter_versions(
                req=Requirement("p>=2.0"),
                cache=c,
                python_version=python_version,
                extend=["*"],
            )
            self.assertEqual([Version("1.0"), Version("2.0")], versions)
