#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import dataclasses
import os
import urllib.parse
import uuid
from pathlib import Path
from typing import Generator

from joker.filesys import utils


@dataclasses.dataclass
class DirectoryBoundToolkit:
    base_dir: Path

    def sha1_rename(self, filename: str) -> str:
        old_path = self.base_dir / filename
        sha1 = utils.checksum_hexdigest(str(old_path), algo='sha1')
        new_path = old_path.with_stem(sha1)
        old_path.rename(new_path)
        return new_path.name

    @staticmethod
    def gen_tmp_filename(ext: str) -> str:
        return f'tmp.{uuid.uuid1()}{ext}'

    def under(self, *paths) -> str:
        return os.path.join(self.base_dir, *paths)

    def relative_to_base_dir(self, path: str) -> str:
        path = os.path.abspath(path)
        return os.path.relpath(path, self.base_dir)

    under_base_dir = under

    def read_as_chunks(self, path: str, length=-1, offset=0, chunksize=65536) \
            -> Generator[bytes, None, None]:
        path = self.under_base_dir(path)
        return utils.read_as_chunks(
            path, length=length,
            offset=offset, chunksize=chunksize,
        )

    def checksum_hexdigest(self, path: str, algo='sha1') -> str:
        path = self.under_base_dir(path)
        return utils.checksum_hexdigest(path, algo=algo)

    def read_as_binary(self, path: str) -> bytes:
        path = self.under_base_dir(path)
        with open(path, 'rb') as fin:
            return fin.read()

    def read_as_base64_data_url(self, path: str) -> str:
        path = self.under_base_dir(path)
        return utils.b64_encode_local_file(path)

    def save_as_file(self, path: str, chunks):
        path = self.under_base_dir(path)
        with open(path, 'wb') as fout:
            for chunk in chunks:
                fout.write(chunk)


class MappedDirectory(DirectoryBoundToolkit):
    def __init__(self, base_dir: str, base_url: str):
        super().__init__(base_dir)
        # Note:
        # urllib.parse.urljoin('/a/b', 'c.jpg') => '/a/c.jpg'
        # urllib.parse.urljoin('/a/b/', 'c.jpg') => '/a/b/c.jpg'
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url

    def __repr__(self) -> str:
        c = self.__class__.__name__
        return '{}({!r}, {!r})'.format(c, self.base_dir, self.base_url)

    def join_url(self, path: str) -> str:
        return urllib.parse.urljoin(self.base_url, path)

    def relative_to_base_url(self, url: str) -> str:
        base_url_path = urllib.parse.urlparse(self.base_url).path
        url_path = urllib.parse.urlparse(url).path
        return os.path.relpath(url_path, base_url_path)

    def convert_local_path_to_url(self, path: str) -> str:
        path = os.path.abspath(path)
        path = self.relative_to_base_dir(path)
        return self.join_url(path)

    def convert_url_to_local_path(self, url: str) -> str:
        path = self.relative_to_base_url(url)
        return self.under(path)
