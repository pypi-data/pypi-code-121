'''
Pygit2 callbacks for the eventual pygit2 shit.

Copyright (c) 2015 - 2022 Rob "N3X15" Nelson <nexisentertainment@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
import os
from typing import Optional

import pygit2
import tqdm


class RemoteProgressCallbacks(pygit2.RemoteCallbacks):
    def __init__(self, credentials=None, certificate=None, ascii: Optional[bool] = None, lazy_tqdm: bool = True):
        super().__init__(credentials=credentials, certificate=certificate)
        self.tqdmObjDownload: tqdm.tqdm = None
        self.tqdmObjIndex: tqdm.tqdm = None
        self.tqdmDeltaIndex: tqdm.tqdm = None
        self.lastStage: str = ''
        self.has_started_up: bool = False
        self.ascii: bool = False
        self.lazy_tqdm: bool = lazy_tqdm

        if ascii is None:
            self.ascii = os.name == 'nt'
        else:
            self.ascii = ascii

    def __enter__(self):
        if not self.lazy_tqdm:
            self.startup()
        return self

    def __exit__(self, x_type, x_value, x_tb):
        self.shutdown()

    def startup(self):
        if self.has_started_up:
            return
        self.tqdmObjDownload = tqdm.tqdm(ascii=self.ascii, desc="Receiving objects")
        self.tqdmObjIndex = tqdm.tqdm(ascii=self.ascii, desc="Indexing objects")
        self.tqdmDeltaIndex = tqdm.tqdm(ascii=self.ascii, desc="Receiving deltas", unit='delta')
        self.has_started_up=True
    def shutdown(self):
        if self.tqdmDeltaIndex is not None:
            self.tqdmDeltaIndex.close()
        if self.tqdmObjIndex is not None:
            self.tqdmObjIndex.close()
        if self.tqdmObjDownload is not None:
            self.tqdmObjDownload.close()

    def _setup_tqdm(self, _tqdm: tqdm.tqdm, message: str, current: int, total: int, unit: str):
        self.startup()
        _tqdm.desc = message
        _tqdm.total = _tqdm.last_print_t = total
        _tqdm.n = _tqdm.last_print_n = current
        _tqdm.unit = unit

    def transfer_progress(self, stats):
        #self.tqdm.clear()
        if stats.total_objects > 0:
            self.startup()
            if self.tqdmObjDownload.total != stats.total_objects:
                self._setup_tqdm(self.tqdmObjDownload, 'Receiving objects', stats.received_objects, stats.total_objects, 'obj')
                self._setup_tqdm(self.tqdmObjIndex, 'Indexing objects', stats.indexed_objects, stats.total_objects, 'obj')
            self.tqdmObjDownload.n = stats.received_objects
            self.tqdmObjIndex.n = stats.indexed_objects
        if stats.total_deltas > 0:
            self.startup()
            if self.tqdmDeltaIndex.total != stats.total_deltas:
                self._setup_tqdm(self.tqdmDeltaIndex, 'Indexing deltas', stats.indexed_deltas, stats.total_deltas, 'delta')
            self.tqdmDeltaIndex.n = stats.indexed_deltas
        if self.has_started_up:
            #self.tqdmDeltaIndex.set_postfix({
            #    'rO': stats.received_objects,
            #    'iO': stats.indexed_objects,
            #    'tO': stats.total_objects,
            #    'iD': stats.indexed_deltas,
            #    'tD': stats.total_deltas,
            #    'recv bytes': stats.received_bytes,
            #}, refresh=False)
            self.tqdmObjDownload.set_postfix_str(f'recv: {stats.received_bytes}B', refresh=False)
            self.tqdmDeltaIndex.update()
            self.tqdmObjIndex.update()
            self.tqdmObjDownload.update()
