'''
QSettings bindings for config.

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
import collections
import os
from tempfile import NamedTemporaryFile

from PyQt5.QtCore import QSettings, QVariant

from .config import ConfigFile, delimset, flattenDict


class QConfig(ConfigFile):

    '''
    Wrapper around QSettings.
    '''

    def __init__(self, filename, default={}, template_dir='.', variables={}, verbose=False):
        super(QConfig, self).__init__(filename, default, template_dir, variables, verbose)

    def _toPyType(self, qvar):
        if qvar.canConvert(0):
            # print('WARN: {} is null?!'.format(qvar.type()))
            return None
        elif qvar.canConvert(QVariant.String) and qvar.type() == QVariant.String:
            return str(qvar.toString())
        elif qvar.canConvert(QVariant.ByteArray):
            return qvar.toByteArray()
        elif qvar.canConvert(QVariant.Int):
            return int(qvar.toInt())
        elif qvar.canConvert(QVariant.Bool):
            return bool(qvar.toBool())
        else:
            return qvar.toPyObject()

    def dump_to_file(self, filename, data):
        if os.path.isfile(filename):
            os.remove(filename)  # Ensure we don't merge.
        qset = QSettings(filename, QSettings.IniFormat)
        for k, v in flattenDict(self.cfg).items():
            #print('{}={}'.format(k, v))
            qset.setValue(k, v)
        del qset  # Forces write

    def load_from_string(self, string):
        '''
        Hacky as fuck.  Writes to temp file on disk, then loads into QSettings.
        '''
        cfg = collections.OrderedDict()
        tmpfilename = ''
        with NamedTemporaryFile(suffix='.ini', delete=False) as f:
            tmpfilename = f.name
            f.write(string)
        qset = QSettings(tmpfilename, QSettings.IniFormat)
        for key in qset.allKeys():
            #print('key: {}'.format(key))
            delimset(cfg, str(key), self._toPyType(qset.value(key)), delim='/')
        del qset
        os.remove(tmpfilename)
        return cfg
