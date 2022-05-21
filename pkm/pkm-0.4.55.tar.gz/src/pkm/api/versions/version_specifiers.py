from __future__ import annotations

from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import List, Optional, Set

from pkm.api.versions.version import Version, StandardVersion, UrlVersion
from pkm.utils.commons import UnsupportedOperationException
from pkm.utils.hashes import HashBuilder
from pkm.utils.iterators import first_or_raise
from pkm.utils.seqs import seq


class VersionSpecifier(ABC):

    def allows_all(self, other: VersionSpecifier) -> bool:
        return self.intersect_with(other) == other

    def allows_any(self, other: VersionSpecifier) -> bool:
        return self.intersect_with(other) is not RestrictAllVersions

    def allows_pre_or_dev_releases(self) -> bool:
        return False

    @abstractmethod
    def allows_version(self, version: Version) -> bool:
        ...

    @abstractmethod
    def union_with(self, other: VersionSpecifier) -> VersionSpecifier:
        ...

    @abstractmethod
    def intersect_with(self, other: VersionSpecifier) -> VersionSpecifier:
        ...

    @abstractmethod
    def inverse(self) -> VersionSpecifier:
        ...

    def difference_from(self, other: VersionSpecifier) -> VersionSpecifier:
        return self.intersect_with(other.inverse())

    @abstractmethod
    def __str__(self) -> str:
        ...

    @abstractmethod
    def __lt__(self, other: VersionSpecifier) -> VersionSpecifier:
        ...

    @abstractmethod
    def __eq__(self, other: VersionSpecifier) -> bool:
        ...

    def __le__(self, other: VersionSpecifier):
        return self == other or self < other

    def __gt__(self, other: VersionSpecifier):
        return other < self

    def __ge__(self, other):
        return other <= self

    @classmethod
    def parse(cls, txt: str) -> VersionSpecifier:
        from pkm.api.versions.version_parser import parse_specifier
        return parse_specifier(txt)

    @classmethod
    def create_range(
            cls, min_: Optional[StandardVersion] = None, max_: Optional[StandardVersion] = None,
            includes_min: bool = False, includes_max: bool = False) -> VersionSpecifier:

        eq = min_ == max_
        assert not (eq and includes_min != includes_max), \
            f"{min_}(min) == {max_}(max) but includes_min != includes_max "

        if min_ is None and max_ is None:
            return AllowAllVersions

        if eq:
            if not includes_min or not includes_max:
                return RestrictAllVersions

            return VersionMatch(min_, includes_min)

        return StandardVersionRange(min_, max_, includes_min, includes_max)


@dataclass(unsafe_hash=True)
class _RestrictAll(VersionSpecifier):

    def inverse(self) -> VersionSpecifier:
        return AllowAllVersions

    def __lt__(self, other):
        return False

    def __eq__(self, other):
        return other is RestrictAllVersions

    def allows_version(self, other: Version) -> bool:
        return False

    def allows_any(self, other: VersionSpecifier) -> bool:
        return False

    def allows_all(self, other: VersionSpecifier) -> bool:
        return False

    def __str__(self):
        return "<none>"

    def union_with(self, other: VersionSpecifier) -> VersionSpecifier:
        return other

    def intersect_with(self, other: VersionSpecifier) -> VersionSpecifier:
        return self


RestrictAllVersions = _RestrictAll()


@dataclass(unsafe_hash=True)
class _AllowAll(VersionSpecifier):

    def inverse(self) -> VersionSpecifier:
        return RestrictAllVersions

    def __lt__(self, other):
        return other is not AllowAllVersions

    def __eq__(self, other):
        return other is AllowAllVersions

    def allows_all(self, other: VersionSpecifier) -> bool:
        if other is RestrictAllVersions:
            return other.allows_all(self)

        return True

    def allows_any(self, other: VersionSpecifier) -> bool:
        if other is RestrictAllVersions:
            return other.allows_any(self)

        return True

    def allows_version(self, other: Version) -> bool:
        return True

    def __str__(self):
        return "*"

    def union_with(self, other: VersionSpecifier) -> VersionSpecifier:
        return self

    def intersect_with(self, other: VersionSpecifier) -> VersionSpecifier:
        return other


AllowAllVersions = _AllowAll()


@dataclass
class VersionsUnion(VersionSpecifier):
    segments: List[VersionSpecifier]

    def __post_init__(self):
        assert len(self.segments) > 1
        assert all(it is not RestrictAllVersions and it is not AllowAllVersions for it in self.segments)
        self.segments.sort()

    def __hash__(self):
        return HashBuilder().ordered_seq(self.segments).build()

    def allows_pre_or_dev_releases(self) -> bool:
        return any(it.allows_pre_or_dev_releases() for it in self.segments)

    def inverse(self) -> VersionSpecifier:
        result = AllowAllVersions
        for segment in self.segments:
            result = result.intersect_with(segment.inverse())
        return result

    def allows_version(self, version: Version) -> bool:
        return any(s.allows_version(version) for s in self.segments)

    def __lt__(self, other: VersionSpecifier):
        return self.segments[0] < other

    def __eq__(self, other: VersionSpecifier):
        return isinstance(other, VersionsUnion) and self.segments == other.segments

    def __str__(self):

        segs = self.segments
        if len(segs) == 2:
            s1, s2 = segs
            if isinstance(s1, StandardVersionRange) and isinstance(s2, StandardVersionRange):
                if not s1.min and not s2.max and s1.max == s2.min:
                    return f"!={s1.max}"
        return seq(segs).str_join('; ')

    def union_with(self, other: VersionSpecifier) -> VersionSpecifier:
        if isinstance(other, (_AllowAll, _RestrictAll)):
            return other.union_with(self)

        new_segments = [*self.segments]
        other_segments = other.segments if isinstance(other, VersionsUnion) else [other]

        while other_segments:
            os = other_segments.pop()
            for i, es in enumerate(new_segments):
                us = os.union_with(es)
                if us is AllowAllVersions:
                    return AllowAllVersions
                if us is RestrictAllVersions:
                    break
                if not isinstance(us, VersionsUnion):
                    other_segments.append(us)
                    del new_segments[i]
                    break
            else:
                new_segments.append(os)

        return VersionsUnion(new_segments)

    def intersect_with(self, other: VersionSpecifier) -> VersionSpecifier:
        if isinstance(other, (_AllowAll, _RestrictAll)):
            return other.intersect_with(self)

        result = RestrictAllVersions
        for segment in self.segments:
            result = result.union_with(segment.intersect_with(other))
        return result


@dataclass
class HetroVersionIntersection(VersionSpecifier):
    blacklist: Set[Version]
    standard_spec: VersionSpecifier

    def __post_init__(self):
        assert len(self.blacklist) > 0, "blacklist must be larger than 0"
        assert self.standard_spec is not RestrictAllVersions

    def allows_pre_or_dev_releases(self) -> bool:
        return self.standard_spec.allows_pre_or_dev_releases() \
               or any(it.is_pre_or_dev_release() for it in self.blacklist)

    def __hash__(self):
        return HashBuilder().unordered_seq(self.blacklist).regular(self.standard_spec).build()

    def allows_version(self, version: Version) -> bool:
        if version in self.blacklist:
            return False

        return not isinstance(version, StandardVersion) or self.standard_spec.allows_version(version)

    def union_with(self, other: VersionSpecifier) -> VersionSpecifier:
        if isinstance(other, (_RestrictAll, _AllowAll, VersionsUnion)):
            return other.union_with(self)

        if isinstance(other, HetroVersionIntersection):
            standard_spec = self.standard_spec.union_with(other.standard_spec)
            if len(other.blacklist.union(self.blacklist)) != len(self.blacklist):
                return standard_spec

            return HetroVersionIntersection.create(
                self.blacklist if len(self.blacklist) < len(other.blacklist) else other.blacklist, standard_spec)

        if isinstance(other, VersionMatch):
            if isinstance(other.version, StandardVersion) and other.allow:
                return HetroVersionIntersection.create(self.blacklist, self.standard_spec.union_with(other))

            blacklist = set(self.blacklist)
            if other.allow:
                blacklist.remove(other.version)
            else:
                blacklist.add(other.version)

            return HetroVersionIntersection.create(blacklist, self.standard_spec)

        if isinstance(other, StandardVersionRange):
            return HetroVersionIntersection.create(self.blacklist, self.standard_spec.union_with(other))

        raise UnsupportedOperationException()

    def intersect_with(self, other: VersionSpecifier) -> VersionSpecifier:
        if isinstance(other, (_RestrictAll, _AllowAll, VersionsUnion)):
            return other.intersect_with(self)

        if isinstance(other, HetroVersionIntersection):
            return HetroVersionIntersection.create(  # yes - union the blacklists
                self.blacklist.union(other.blacklist), self.standard_spec.intersect_with(other.standard_spec))

        if isinstance(other, VersionMatch):
            if isinstance(other.version, StandardVersion) and other.allow:
                if self.standard_spec.allows_version(other.version) and other.version not in self.blacklist:
                    return other
                return RestrictAllVersions

            if other.allow:
                if other.version in self.blacklist:
                    return RestrictAllVersions
                return other

            return HetroVersionIntersection.create({*self.blacklist, other.version}, self.standard_spec)

        if isinstance(other, StandardVersionRange):
            return HetroVersionIntersection.create(self.blacklist, self.standard_spec.intersect_with(other))

        raise UnsupportedOperationException()

    def inverse(self) -> VersionSpecifier:
        union = [*(VersionMatch(it) for it in self.blacklist)]
        if self.standard_spec is not AllowAllVersions:
            union.append(self.standard_spec.inverse())
        return VersionsUnion(union)

    def __str__(self) -> str:
        result = ", ".join(f"!={it}" for it in self.blacklist)
        if self.standard_spec is not AllowAllVersions:
            result += f", {self.standard_spec}"
        return result

    def __lt__(self, other: VersionSpecifier) -> bool:
        if isinstance(other, (_RestrictAll, _AllowAll, VersionsUnion)):
            return not self >= other

        if isinstance(other, HetroVersionIntersection):
            if self.blacklist == other.blacklist:
                return self.standard_spec < other.standard_spec
            return sorted(self.blacklist) < sorted(other.blacklist)

        if isinstance(other, VersionMatch):
            if isinstance(other.version, StandardVersion):
                return self.standard_spec < other
            return other.allow or sorted(self.blacklist) < [other.version]

        if isinstance(other, StandardVersionRange):
            return self.standard_spec < other

        raise UnsupportedOperationException()

    def __eq__(self, other: VersionSpecifier) -> bool:
        return isinstance(other, HetroVersionIntersection) \
               and self.blacklist == other.blacklist and self.standard_spec == other.standard_spec

    @classmethod
    def create(cls, blacklist: Set[Version], standard_spec: VersionSpecifier) -> VersionSpecifier:
        blacklist = {it for it in blacklist if not isinstance(it, StandardVersion) or standard_spec.allows_version(it)}

        if standard_spec is RestrictAllVersions:
            return RestrictAllVersions
        if len(blacklist) == 0:
            return standard_spec
        if len(blacklist) == 1 and standard_spec is AllowAllVersions:
            return VersionMatch(first_or_raise(blacklist), False)

        return HetroVersionIntersection(blacklist, standard_spec)


@dataclass(unsafe_hash=True)
class VersionMatch(VersionSpecifier):
    version: Version
    allow: bool = True

    def allows_pre_or_dev_releases(self) -> bool:
        return self.allow and self.version.is_pre_or_dev_release()

    def inverse(self) -> VersionSpecifier:
        return VersionMatch(self.version, not self.allow)

    def __lt__(self, other: VersionSpecifier):
        if isinstance(other, (_RestrictAll, _AllowAll, VersionsUnion, HetroVersionIntersection)):
            return not self >= other

        if isinstance(other, VersionMatch):
            if self == other:
                return False
            if self.allow:
                return not other.allow
            return other.allow and self.version < other.version

        if isinstance(other, StandardVersionRange):
            if isinstance(self.version, StandardVersion):
                if self.allow:
                    return other.min and self.version < other.min
                return bool(other.min)

            return True  # uid versions comes before any standard ones

        raise NotImplemented()

    def __eq__(self, other: VersionSpecifier) -> bool:
        return isinstance(other, VersionMatch) \
               and self.allow == other.allow and self.version == other.version

    def allows_version(self, version: Version) -> bool:
        if not self.version.is_local():
            version = version.without_local()

        if self.allow:
            return self.version == version
        return self.version != version

    def __str__(self):
        v, a = self.version, self.allow

        if isinstance(v, UrlVersion):
            return f'@{v}' if a else f'!@{v}'
        elif isinstance(v, StandardVersion):
            return f'=={v}' if a else f'!={v}'
        return f'==={v}' if a else f'!=={v}'

    def union_with(self, other: VersionSpecifier) -> VersionSpecifier:
        if isinstance(other, (_RestrictAll, _AllowAll, HetroVersionIntersection, VersionsUnion)):
            return other.union_with(self)

        if isinstance(other, VersionMatch):
            if self == other:
                return self

            if self.version == other.version:
                if self.allow != other.allow:
                    return AllowAllVersions

        if isinstance(other, StandardVersionRange):
            if other.allows_version(self.version):
                return other if self.allow else AllowAllVersions

            if not self.allow:
                return self

            if not other.includes_min and self.version == other.min:
                return StandardVersionRange(other.min, other.max, True, other.includes_max)
            if not other.includes_max and self.version == other.max:
                return StandardVersionRange(other.min, other.max, other.includes_min, True)

        return VersionsUnion([self, other])

    def intersect_with(self, other: VersionSpecifier) -> VersionSpecifier:
        if isinstance(other, (_RestrictAll, _AllowAll, HetroVersionIntersection, VersionsUnion)):
            return other.intersect_with(self)

        if isinstance(other, VersionMatch):
            if self == other:
                return self

            my_ver, ot_ver = self.version, other.version
            if my_ver.is_local() != ot_ver.is_local():
                my_ver, ot_ver = my_ver.without_local(), ot_ver.without_local()

            if self.allow and other.allow:
                if my_ver == ot_ver:
                    return self if self.version.is_local() else other
                return RestrictAllVersions
            if self.allow or other.allow:
                if my_ver == ot_ver:
                    return RestrictAllVersions
                return self if self.allow else other
            return HetroVersionIntersection({self.version, other.version}, AllowAllVersions)

        if isinstance(other, StandardVersionRange) and isinstance(self.version, StandardVersion):
            if other.allows_version(self.version):
                if self.allow:
                    return self
                return HetroVersionIntersection({self.version}, other)

        return RestrictAllVersions if self.allow else other


@dataclass(unsafe_hash=True)
class StandardVersionRange(VersionSpecifier):
    min: Optional[StandardVersion]
    max: Optional[StandardVersion]
    includes_min: bool
    includes_max: bool

    def __post_init__(self):
        assert self.min or self.max, "either min or max should be provided"
        assert not self.includes_min or self.min, "cannot include min if min is not provided"
        assert not self.includes_max or self.max, "cannot include max if max is not provided"
        assert not self.min or not self.max or self.min < self.max, f"min ({self.min}) must be < max ({self.max}) "

    def allows_pre_or_dev_releases(self) -> bool:
        return (self.min and self.min.is_pre_or_dev_release()) or (self.max and self.max.is_pre_or_dev_release())

    def inverse(self) -> VersionSpecifier:
        parts = []
        if self.min:
            parts.append(VersionSpecifier.create_range(None, self.min, False, self.min and not self.includes_min))
        if self.max:
            parts.append(VersionSpecifier.create_range(self.max, None, self.max and not self.includes_max, False))

        if len(parts) == 1:
            return parts[0]
        return parts[0].union_with(parts[1])

    def __lt__(self, other):
        if isinstance(other, (_RestrictAll, _AllowAll, VersionsUnion, HetroVersionIntersection, VersionMatch)):
            return not self >= other

        if isinstance(other, StandardVersionRange):
            if self == other:
                return False

            if self.min and other.min:
                if self.min != other.min:
                    return self.min < other.min
                elif self.includes_min != other.includes_min:
                    return other.includes_min
            elif self.min or other.min:
                return bool(other.min)

            if self.max and other.max:
                if self.max != other.max:
                    return self.max < other.max
                return other.includes_max

            return bool(self.max)

        raise NotImplemented()

    def __eq__(self, other):
        return isinstance(other, StandardVersionRange) and self.includes_min == other.includes_min \
               and self.includes_max == other.includes_max and self.min == other.min and self.max == other.max

    def __str__(self):
        res = ''
        if self.min is not None:
            res += '>'
            if self.includes_min:
                res += '='
            res += str(self.min)

        if self.max is not None:
            if res:
                res += ', '
            res += '<'
            if self.includes_max:
                res += '='
            res += str(self.max)

        return res

    def _union_with(self, other: StandardVersionRange) -> VersionSpecifier:
        if other < self:
            return other._union_with(self)

        imin, imax = self.includes_min, other.includes_max
        if not other.min or not self.max or other.min < self.max:
            if self.min == other.min:
                imin = self.includes_min or other.includes_min
            if self.max == other.max:
                imax = self.includes_max or other.includes_max
        elif (not self.includes_max and not other.includes_min) or other.min != self.max:
            return VersionsUnion([self, other])

        return VersionSpecifier.create_range(self.min, other.max, imin, imax)

    def union_with(self, other: VersionSpecifier) -> VersionSpecifier:
        if isinstance(other, (_RestrictAll, _AllowAll, VersionsUnion, HetroVersionIntersection, VersionMatch)):
            return other.union_with(self)

        if isinstance(other, StandardVersionRange):
            if self == other:
                return self
            return self._union_with(other)

        raise NotImplemented()

    def _intersect_with(self, other: StandardVersionRange) -> VersionSpecifier:
        if other < self:
            return other._intersect_with(self)

        if not other.min or not self.max or other.min < self.max:
            imin, imax = other.includes_min, self.includes_max
            if self.min == other.min:
                imin = self.includes_min and other.includes_min
            if self.max == other.max:
                imax = self.includes_max and other.includes_max

            max_ = self.max
            if not max_ or (other.max and self.max > other.max):
                max_, imax = other.max, other.includes_max

            return VersionSpecifier.create_range(other.min, max_, imin, imax)
        if self.includes_max and other.includes_min and self.max == other.min:
            return VersionMatch(self.max, True)

        return RestrictAllVersions

    def intersect_with(self, other: VersionSpecifier) -> VersionSpecifier:
        if isinstance(other, (_RestrictAll, _AllowAll, VersionsUnion, HetroVersionIntersection, VersionMatch)):
            return other.intersect_with(self)

        if isinstance(other, StandardVersionRange):
            if self == other:
                return self

            return self._intersect_with(other)
        raise NotImplemented()

    def allows_version(self, version: Version) -> bool:
        min_, max_ = self.min, self.max
        if (min_ is not None and self.includes_min and min_ == version) \
                or (max_ is not None and self.includes_max and max_ == version):
            return True

        if version.is_post_release() and (min_ is None or not min_.is_post_release()):
            return False

        return (min_ is None or min_ < version) and (max_ is None or version < max_)
