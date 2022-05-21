from dataclasses import replace
from pathlib import Path
from typing import List

from pkm.api.versions.version import Version, NamedVersion, StandardVersion, UrlVersion
from pkm.api.versions.version_specifiers import VersionSpecifier, AllowAllVersions, VersionMatch
from pkm.utils.parsers import SimpleParser


def parse_version(version_str: str) -> Version:
    try:
        lowered_vstr = version_str.lower()
        if '://' in lowered_vstr:
            return UrlVersion.parse(lowered_vstr)

        return VersionParser(lowered_vstr).read_version()
    except ValueError:
        ...
    return NamedVersion(version_str)


def parse_specifier(specifier_str: str) -> VersionSpecifier:
    return VersionParser(specifier_str.lower()).read_specifier()


_PRE_RELEASE_TYPE_NORMALIZER = {
    'a': 'a', 'b': 'b', 'rc': 'rc', 'c': 'rc', 'alpha': 'a', 'beta': 'b', 'preview': 'rc'
}


class VersionParser(SimpleParser):

    def read_version(self) -> StandardVersion:
        self.match_ws()

        wrapping_brakets = self.match("(", "")
        wrapping_quotes = self.match("'", "") or self.match("\"", "")

        self.match('v')

        epoch = None
        n = self.read_digits()
        if self.match('!'):
            epoch = int(n)
            n = self.read_digits()

        release: List[int] = [int(n)]
        while self.match('.') and self.is_not_empty() and self.peek().isdigit():
            release.append(int(self.read_digits()))

        pre_release = None
        # pre_release_type = self.peek_prev() != '.' and self.match_any(*_PRE_RELEASE_TYPE_NORMALIZER.keys())
        pre_release_type = self.match_any(*_PRE_RELEASE_TYPE_NORMALIZER.keys())
        if pre_release_type:
            self.match_any('.', '-', '_')
            pre_release_num = 0 if not self.peek().isdigit() else int(self.read_digits())
            pre_release = (_PRE_RELEASE_TYPE_NORMALIZER[pre_release_type], pre_release_num)

        post_release = None

        if (prev := self.peek_prev()).isdigit() or prev in _PRE_RELEASE_TYPE_NORMALIZER:
            self.match_any('.', '-', '_')
        if self.match_any('post', 'r', 'rev') or (self.peek_prev() == '-' and self.peek().isdigit()):
            self.match('-')
            post_release = 0 if not self.peek().isdigit() else int(self.read_digits())

        dev_release = None
        if self.peek_prev().isdigit():
            self.match_any('.', '-', '_')
        if self.match('dev'):
            dev_release = 0 if not self.peek().isdigit() else int(self.read_digits())

        local_label = None
        if self.match('+'):
            local_label = self.until(lambda i, s: s[i] not in ".-_" and not s[i].isalnum())
            local_label = local_label.translate(local_label.maketrans('-_', '..'))

        if self.peek_prev() == '.':
            self.position -= 1

        self.match_ws()

        if wrapping_quotes:
            self.match_or_err(wrapping_quotes, f"expecting closing quote: [{wrapping_quotes}]")
        if wrapping_brakets:
            self.match_or_err(')', f"expecting closing quote: [)]")
        self.match_ws()

        return StandardVersion(release=tuple(release), epoch=epoch, pre_release=pre_release, post_release=post_release,
                               dev_release=dev_release, local_label=local_label)

    # noinspection PyShadowingBuiltins
    def _read_single_specifier(self) -> VersionSpecifier:
        self.match_ws()

        if self.match('*'):
            return AllowAllVersions

        if self.match('@'):
            self.match_ws()
            url = self.until(lambda i, s: s[i].isspace())
            if "://" not in url:
                url = Path(url).resolve().as_uri()

            return VersionMatch(UrlVersion.parse(url))

        if self.match('==='):
            self.match_ws()
            version_str = self.until(lambda i, t: t[i].isspace() or t[i] == ',')
            return VersionMatch(NamedVersion(version_str))

        exclusion_inclusion = self.match_any('==', '!=')
        if exclusion_inclusion:
            self.match_ws()
            version = self.read_version()
            if self.match('.*'):
                result = VersionSpecifier.create_range(
                    version, replace(version, release=version.release[:-1] + (version.release[-1] + 1,)), True, False)
            else:
                if isinstance(version, StandardVersion):
                    result = VersionSpecifier.create_range(version, version, True, True)
                else:
                    result = VersionMatch(version)

            if exclusion_inclusion == '!=':
                return result.inverse()
            return result

        if self.match('~='):
            self.match_ws()
            version = self.read_version()

            if len(version.release) == 1:
                raise ValueError(f"Illegal version specifier, ~= {version}")

            return VersionSpecifier.create_range(
                version, replace(
                    version, release=version.release[:-2] + (version.release[-2] + 1, 0), pre_release=None,
                    post_release=None, dev_release=None, local_label=None),
                True, False)

        comparison = self.match_any('>=', '>', '<=', '<')
        if comparison:
            self.match_ws()
            version = self.read_version()
            min, max, imin, imax = None, None, False, False

            if comparison[0] == '>':
                min, imin = version, len(comparison) > 1
            else:
                max, imax = version, len(comparison) > 1

            self.match(".*")  # version spec can end (un-needed-ly for comparison operators other than ==/!=) with .*

            return VersionSpecifier.create_range(min, max, imin, imax)

        self.raise_err('unknown operator')

    def read_specifier(self):
        self.match_ws()
        paren = self.match('(')

        specifier = AllowAllVersions
        while self.is_not_empty():
            specifier = specifier.intersect_with(self._read_single_specifier())
            self.match_ws()
            if not self.match(',') and self.is_not_empty():
                if not paren or self.match(')'):
                    break
                self.raise_err("expecting comma (',')")

        return specifier
