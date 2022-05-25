#!/usr/bin/python3

# Mediadex: Index media metadata into opensearch
# Copyright (C) 2019-2022  Joni Harker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import hashlib
import logging

import chardet
from pymediainfo import MediaInfo


class FileInfo:
    def __init__(self, f, b):
        self.log = logging.getLogger('mediadex.fileinfo')
        self.hashlib = hashlib.sha384()
        self.fullpath = f
        self.basepath = b
        self.mediainfo = None
        self.fingerprint = None

    def dumpData(self):
        output = {}
        output['fullpath'] = self.fullpath
        output['basepath'] = self.basepath
        output['mediainfo'] = self.mediainfo
        output['fingerprint'] = self.fingerprint

        return output

    def hashFile(self):
        # Magic numbers for file chunking
        chunk_size = 24576
        chunk_count = 128

        with open(self.fullpath, 'rb') as f:
            try:
                for _ in range(chunk_count):
                    chunk = f.read(chunk_size)
                    if chunk:
                        self.hashlib.update(chunk)
            except Exception as exc:
                if self.log.isEnabledFor(logging.INFO):
                    self.log.exception(exc)
                else:
                    self.log.warn(str(exc))

        self.fingerprint = self.hashlib.hexdigest()

    def parseMediaInfo(self):
        f = self.fullpath
        try:
            self.mediainfo = MediaInfo.parse(f).to_data()
        except FileNotFoundError:
            _enc = f.encode('utf-8', 'surrogateescape')
            charset = chardet.detect(f).get('encoding')
            self.log.info("chardet found: {}".format(charset))

            try:
                _f = _enc.decode(charset)
                self.mediainfo = MediaInfo.parse(_f).to_data()
            except FileNotFoundError:
                self.log.warning("chardet failure: {}".format(_f))

        except Exception as exc:
            if self.log.isEnabledFor(logging.INFO):
                self.log.exception(exc)
            else:
                self.log.warn(str(exc))

        finally:
            if not self.mediainfo:
                _f = f.encode('utf-8', 'surrogateescape')
                raise IOError("Could not open {}".format(_f))
