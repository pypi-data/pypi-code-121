from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Tuple, Optional, Literal
import re

from pkm.utils.commons import UnsupportedOperationException
from pkm.utils.http.http_client import Url

VERSION_URL_RX = re.compile(r"((?P<repo>\w+)\+)?(?P<url>.*)")


class Version(ABC):
    @abstractmethod
    def is_pre_or_dev_release(self) -> bool:
        ...

    @abstractmethod
    def is_post_release(self) -> bool:
        ...

    @abstractmethod
    def is_local(self) -> bool:
        ...

    def without_patch(self):
        return self

    def without_local(self) -> "Version":
        return self

    def __lt__(self, other: "Version") -> bool:
        return _less(self, other)

    @abstractmethod
    def __eq__(self, other) -> bool:
        ...

    @classmethod
    def parse(cls, txt: str) -> "Version":
        from pkm.api.versions.version_parser import parse_version
        return parse_version(txt)


@dataclass(frozen=True)
class UrlVersion(Version):
    url: str
    _protocol: str
    _schema: str

    @property
    def protocol(self) -> str:
        return self._protocol or self._schema

    def is_pre_or_dev_release(self) -> bool:
        return False

    def is_post_release(self) -> bool:
        return False

    def is_local(self) -> bool:
        return False

    def __eq__(self, other) -> bool:
        return isinstance(other, UrlVersion) and self.protocol == other.protocol and self.url == other.url

    def __str__(self):
        if self._protocol:
            return self._protocol + "+" + self.url
        return self.url

    def __repr__(self):
        return str(self)

    @classmethod
    def parse(cls, txt: str) -> UrlVersion:
        match = VERSION_URL_RX.match(txt.lower())
        parsed_url = Url.parse(match.group('url'))
        return cls(match.group('url'), match.group('repo'), parsed_url.scheme)


@dataclass(frozen=True)
class NamedVersion(Version):
    name: str

    def is_pre_or_dev_release(self) -> bool:
        return False

    def is_post_release(self) -> bool:
        return False

    def is_local(self) -> bool:
        return False

    def __eq__(self, other) -> bool:
        return isinstance(other, NamedVersion) and self.name == other.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"NamedVersion({str(self)})"


@dataclass(frozen=True, repr=False)
class StandardVersion(Version):
    release: Tuple[int, ...]
    epoch: Optional[int] = None
    pre_release: Optional[Tuple[Literal['a', 'b', 'rc'], int]] = None
    post_release: Optional[int] = None
    dev_release: Optional[int] = None
    local_label: Optional[str] = None

    def without_local(self) -> "StandardVersion":
        if self.is_local():
            return replace(self, local_label=None)
        return self

    def without_patch(self):
        if len(self.release) > 2:
            return replace(self, release=self.release[:2])
        return self

    def standartize(self) -> "StandardVersion":
        release = self.release
        while len(release) > 1 and release[-1] == 0:
            release = release[:-1]

        post, dev = self.post_release, self.dev_release
        post = None if post == 0 else post
        dev = None if dev == 0 else dev

        return replace(self, release=release, post_release=post, dev_release=dev)

    def __hash__(self):
        s = self.standartize()
        return hash((s.release, s.epoch, s.dev_release, s.post_release, s.pre_release, s.local_label))

    def is_pre_or_dev_release(self) -> bool:
        return self.pre_release is not None or self.dev_release is not None

    def is_post_release(self) -> bool:
        return self.post_release is not None

    def is_local(self) -> bool:
        return self.local_label is not None

    def bump(self, particle: str) -> Version:
        """
        bump up this version
        :param particle: the particle of the version to bump, can be any of: major, minor, patch, a, b, rc
        :return: the new version after the bump
        """

        version: Version = self
        if not isinstance(version, StandardVersion) or not len(version.release) == 3:
            raise UnsupportedOperationException("cannot bump version that does not follow the semver semantics")

        def update_release(v: StandardVersion, new_release: Tuple[int, ...], ) -> Version:
            return replace(v, release=new_release,
                           pre_release=None, post_release=None, dev_release=None, local_label=None)

        def bump_release(v: StandardVersion, p: str) -> Optional[Version]:
            release = v.release
            if p == 'major':
                return update_release(v, (release[0] + 1, 0, 0))
            elif p == 'minor':
                return update_release(v, (release[0], release[1] + 1, 0))
            elif p == 'patch':
                return update_release(v, (release[0], release[1], release[2] + 1))
            else:
                return None

        def bump_pre_release(v: StandardVersion, p: str) -> Optional[Version]:
            pre_release = v.pre_release
            if pre_release:
                if pre_release[0] > p:
                    v = bump_release(v, 'patch')
                    pre_release = None
                elif pre_release[0] < p:
                    pre_release = (p, 0)
                else:
                    pre_release = (p, pre_release[1] + 1)
            else:
                pre_release = (p, 0)

            return replace(v, pre_release=pre_release)

        new_version = bump_release(version, particle) or bump_pre_release(version, particle)
        if not new_version:
            raise ValueError(f"unknown version particle: {particle}")

        return new_version

    def __str__(self):
        vstring = ''
        if self.epoch is not None:
            vstring += f'{self.epoch}!'
        vstring += '.'.join(str(n) for n in self.release)
        if self.pre_release is not None:
            vstring += ''.join(str(it) for it in self.pre_release)
        if self.post_release is not None:
            vstring += f'.post{self.post_release}'
        if self.dev_release is not None:
            vstring += f'.dev{self.dev_release}'
        if self.local_label is not None:
            vstring += f'+{self.local_label}'

        return vstring

    def __repr__(self):
        return str(self)

    def __le__(self, other):
        return other == self or self < other

    def equals_to(self, other, compare_locals: bool):
        """
        compare two version, with/without taking into consideration the local part
        :param compare_locals: if true, will take into consideration the local part
        :param other: the version to compare to
        """

        if not isinstance(other, StandardVersion):
            return False

        v1, v2 = StandardVersion.normalized(self, other)
        return (v1.epoch or 0) == (other.epoch or 0) \
               and v1.release == v2.release \
               and v1.pre_release == v2.pre_release \
               and v1.post_release == v2.post_release \
               and v1.dev_release == v2.dev_release \
               and (not compare_locals or self.local_label == other.local_label)  # noqa

    def __eq__(self, other):
        return self.equals_to(other, True)

    @staticmethod
    def normalized(v1: "StandardVersion", v2: "StandardVersion") -> Tuple["StandardVersion", "StandardVersion"]:
        v1rel, v2rel = v1.release, v2.release  # noqa
        rlen = max(len(v1rel), len(v2rel))  # noqa

        if len(v1rel) != rlen:
            v1rel += (0,) * (rlen - len(v1rel))
        if len(v2rel) != rlen:
            v2rel += (0,) * (rlen - len(v2rel))

        return ((v1 if v1rel == v1.release else replace(v1, release=v1rel)),
                (v2 if v2rel == v2.release else replace(v2, release=v2rel)))

    @classmethod
    def parse(cls, txt: str) -> "StandardVersion":
        from pkm.api.versions.version_parser import VersionParser
        return VersionParser(txt.lower()).read_version()


def _less(v1: Version, v2: Version) -> bool:
    swap = False

    # order: [urls] [named-versions] [standard-versions]

    if isinstance(v1, UrlVersion) or (swap := isinstance(v2, UrlVersion)):
        if swap: return not _less(v2, v1)  # noqa

        if isinstance(v2, UrlVersion):
            return str(v1) < str(v2)

        return True

    if isinstance(v1, NamedVersion) or (swap := isinstance(v2, NamedVersion)):
        if swap: return not _less(v2, v1)  # noqa

        if isinstance(v2, NamedVersion):
            return v1.name < v2.name

        return True

    # must be standard version
    v1: StandardVersion
    v2: StandardVersion

    if (v1.epoch or 0) != (v2.epoch or 0):
        return (v1.epoch or 0) < (v2.epoch or 0)

    v1, v2 = StandardVersion.normalized(v1, v2)
    for s, o in zip(v1.release, v2.release):
        if s == o:
            continue
        return s < o

    if v1.dev_release != v2.dev_release:
        if (v1.dev_release is None) ^ (v2.dev_release is None):
            return v2.dev_release is None

        if v1.dev_release != v2.dev_release:
            return v1.dev_release < v2.dev_release

    if v1.pre_release != v2.pre_release:
        if (v1.pre_release is None) ^ (v2.pre_release is None):
            return v2.pre_release is None

        for s, o in zip(v1.pre_release, v2.pre_release):
            if s == o: continue  # noqa
            return s < o

    if v1.post_release != v2.post_release:
        if (v1.post_release is None) ^ (v2.post_release is None):
            return v1.post_release is None

        s, o = v1.post_release, v2.post_release
        if s != o:
            return s < o

    my_local_segments = (v1.local_label or "").split('.')
    other_local_segments = (v2.local_label or "").split('.')

    for m, o in zip(my_local_segments, other_local_segments):
        if m == o:
            continue

        m_num, o_num = m.isnumeric(), o.isnumeric()
        if m_num and o_num:
            return int(m_num) < int(o_num)
        if m_num or o_num:
            return o_num

        return m < o

    return len(my_local_segments) < len(other_local_segments)
