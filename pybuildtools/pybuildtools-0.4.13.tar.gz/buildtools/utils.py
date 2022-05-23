'''
General-Purpose Utilities.

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
import time
import hashlib
import sys
import mimetypes
import binascii
import mmap

def getClass(thing):
    return thing.__class__


def getClassName(thing):
    return getClass(thing).name


def bool2yn(b):
    return 'Y' if b else 'N'

def is_python_3():
    return sys.version_info[0] >= 3

if is_python_3():
    def bytes2str(b):
        if isinstance(b,bytes):
            return b.decode('utf-8')
        else:
            return str(b)
else:
    def bytes2str(b):
        return str(b)

def hashfile(afile, hasher, blocksize=65536):
    if isinstance(afile, str):
        with open(afile, 'rb') as f:
            return hashfile(f,hasher,blocksize)
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()


def md5sum(filename, blocksize=65536):
    with open(filename, 'rb') as f:
        return hashfile(f, hashlib.md5())


def sha256sum(filename, blocksize=65536):
    with open(filename, 'rb') as f:
        return hashfile(f, hashlib.sha256())

def img2blob(filename):
    mime, _ = mimetypes.guess_type(filename)
    with open(filename, 'rb') as fp:
        data64 = binascii.b2a_base64(fp.read())
    return 'data:%s;base64,%s' % (mime, data64.decode('ascii'))


def get_num_lines(file_path):
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines

current_milli_time = lambda: int(round(time.time() * 1000))
