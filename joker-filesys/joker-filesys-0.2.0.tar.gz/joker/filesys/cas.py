#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Iterable

from joker.filesys import utils
from joker.filesys.utils import PathLike


@dataclass
class ContentAddressedStorage:
    base_dir: PathLike
    dist_dirs: dict[str, PathLike] = field(default_factory=dict)
    hash_algo: str = 'sha256'
    dir_depth: int = 2
    chunksize: int = 4096

    @classmethod
    def from_config(cls, cfg: dict | str):
        if isinstance(cfg, str):
            return cls(cfg)
        return cls(**cfg)

    @cached_property
    def _prefix_lengths(self) -> list[int]:
        lengths = {len(prefix) for prefix in self.dist_dirs}
        lengths = list(lengths)
        lengths.sort(reverse=True)
        return lengths

    @cached_property
    def _base_path(self) -> Path:
        return Path(self.base_dir)

    def _locate_dir(self, cid: str) -> Path:
        if not self.dist_dirs:
            return self._base_path
        for length in self._prefix_lengths:
            prefix = cid[:length]
            if prefix in self.dist_dirs:
                return Path(self.dist_dirs[prefix])
        return self._base_path

    def locate(self, cid: str) -> Path:
        dir_ = self._locate_dir(cid)
        names = utils.spread_by_prefix(cid, self.dir_depth)
        return dir_.joinpath(*names)

    def walk(self) -> Iterable[tuple]:
        yield from os.walk(self.base_dir)
        for dir_ in self.dist_dirs.values():
            yield from os.walk(dir_)

    def iter_paths(self) -> Iterable[str]:
        for dirpath, _, filenames in self.walk():
            for filename in filenames:
                yield os.path.join(dirpath, filename)

    def iter_cids(self) -> Iterable[str]:
        for triple in self.walk():
            yield from triple[2]

    def exists(self, cid: str) -> bool:
        path = self.locate(cid)
        return path.is_file()

    def delete(self, cid: str):
        path = self.locate(cid)
        if path.is_file():
            path.unlink(missing_ok=True)

    def load(self, cid: str) -> Iterable[bytes]:
        path = self.locate(cid)
        if not path.is_file():
            return
        with open(path, 'rb') as fin:
            chunk = fin.read(self.chunksize)
            while chunk:
                yield chunk
                chunk = fin.read(self.chunksize)

    def guess_content_type(self, cid: str):
        with open(self.locate(cid), 'rb') as fin:
            return utils.guess_content_type(fin.read(64))

    def check_integrity(self, cid: str) -> bool:
        ho = hashlib.new(self.hash_algo)
        for chunk in self.load(cid):
            ho.update(chunk)
        return ho.hexdigest() == cid

    def save(self, chunks: Iterable[bytes]) -> str:
        ho = hashlib.new(self.hash_algo)
        tmp = self._base_path / utils.gen_unique_filename()
        try:
            with open(tmp, 'wb') as fout:
                for chunk in chunks:
                    ho.update(chunk)
                    fout.write(chunk)
            cid = ho.hexdigest()
            utils.moves(tmp, self.locate(cid))
            ho = None
        finally:
            if ho is not None:
                tmp.unlink(missing_ok=True)
        return cid


__all__ = ['ContentAddressedStorage']
