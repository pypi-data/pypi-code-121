#!/usr/bin/env python3

# standards
from dataclasses import dataclass, replace
from hashlib import md5
import re
from typing import Optional, Tuple, Union

# 3rd parties
from requests import PreparedRequest


UserSpecifiedCacheKey = Union['CacheKey', Tuple[str, ...], str]


@dataclass(frozen=True, order=True)
class CacheKey:

    parts: Tuple[str, ...]
    sequence_num: int = 0

    @property
    def path_parts(self) -> Tuple[str, ...]:
        parts = [
            # chars that *must* be escaped:
            #  * all chars that aren't valid in Windows file names
            #  * slashes, backslashes and null chars
            #  * dots, so that ".4" at the end unambiguously identifies a sequence num (and also avoids directory traversal vulns)
            re.sub(r'[^\w\-]', lambda m: f'%{ord(m.group()):02X}', part)
            for part in self.parts
        ]
        if self.sequence_num > 0:
            parts[-1] += f'.{self.sequence_num}'
        return tuple(parts)

    @property
    def unique_str(self) -> str:
        # NB the string we return isn't for use in paths, so we can use '/' as the separator regardless of platform. Slashes have
        # been removed from the parts, so this is unambiguous.
        return '/'.join(self.path_parts)

    def next_in_sequence(self):
        return replace(self, sequence_num=self.sequence_num + 1)

    @classmethod
    def from_path_parts(cls, parts):
        seq_match = re.search(r'\.(\d+)$', parts[-1])
        if seq_match:
            sequence_num = int(seq_match.group(1))
            parts[-1] = parts[-1][:seq_match.start()]
        else:
            sequence_num = 0
        return cls(
            parts=tuple(
                re.sub(r'%([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), p)
                for p in parts
            ),
            sequence_num=sequence_num,
        )

    @classmethod
    def compute(cls, preq: PreparedRequest) -> 'CacheKey':
        # NB we don't normalise the order of the `params` dict or `data` dict. If running in Python 3.6+, where dicts preserve
        # their insertion order, multiple calls from the same code, where the params are defined in the same order, will hit the
        # same cache key. In previous versions, maybe not, so in 3.5 and before params and body should be serialised before being
        # sent to Hublot.
        headers = sorted(
            (key.title(), value)
            for key, value in preq.headers.items()
        )
        key = (
            preq.method,
            preq.url,
            headers,
            preq.body,
        )
        # Shortening to 16 chars means it's easier to copy-paste, takes less space in the terminal, etc. Seems like a flimsy reason
        # for increasing the chances of a collision, but at 2^64 bits these chances are still comfortably negligible.
        hashed = md5(repr(key).encode('UTF-8')).hexdigest()[:16]
        return cls((hashed[:3], hashed[3:]))

    @classmethod
    def parse(cls, user_specified_key: Optional[UserSpecifiedCacheKey]):
        if isinstance(user_specified_key, CacheKey):
            return user_specified_key
        elif isinstance(user_specified_key, tuple):
            return cls(user_specified_key)
        elif isinstance(user_specified_key, str):
            return cls(tuple(user_specified_key.strip('/').split('/')))
        else:
            raise TypeError(repr(user_specified_key))
