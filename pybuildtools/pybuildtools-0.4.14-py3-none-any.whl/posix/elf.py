'''
ELF Utilities

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

@author: Rob
Created on Feb 13, 2015
'''
import os, re, sys, glob

from buildtools.bt_logging import log

from elftools.elf.elffile import ELFFile
from elftools.common import exceptions
from elftools.common.exceptions import ELFError
from elftools.common.py3compat import bytes2str
from elftools.elf.dynamic import DynamicSection
from elftools.elf.descriptions import describe_ei_class

class ELFInfo:
    LDPATHS = None
    def __init__(self, path, ld_library_path=None):
        self.path = path

        self.needed = []
        self.rpath = []
        self.runpath = []
        self.interpreter = None

        self.f = open(path, 'rb')
        self.elf = ELFFile(self.f)

    def Close(self):
        self.f.close()

    def Load(self):
        libs = []
        for segment in self.elf.iter_segments():
            if segment.header.p_type == 'PT_INTERP':
                self.interpreter = segment.get_interp_name()
                self.needed += [os.path.normpath(self.interpreter)]
            elif segment.header.p_type == 'PT_DYNAMIC':
                for tag in segment.iter_tags():
                    if tag.entry.d_tag == 'DT_NEEDED':
                        libs += [tag.needed]
                    # if tag.entry.d_tag == 'DT_RPATH':
                    #    self.setRawRPath(tag.rpath)
                    # if tag.entry.d_tag == 'DT_RUNPATH':
                    #    self.setRawRunPath(tag.runpath)
        for lib in libs:
            self.needed += [self.findLib(lib)]

    def setRawRunPath(self, runpath_data):
        if len(self.rpath) > 0:
            self.rpath = []
        self.runpath = self._ParseLdPaths(runpath_data)

    def setRawRPath(self, rpath_data):
        if len(self.runpath) > 0:
            return
        self.rpath = self._ParseLdPaths(rpath_data)

    def findLib(self, givenname):
        if self.LDPATHS is None:
            self.LDPATHS = ldpaths()
            log.info('Search ldpaths: ' + repr(self.LDPATHS))
        myclass=self.getElfClass()
        for path in self.LDPATHS:
            lib = path + os.sep + givenname
            if os.path.exists(lib):
                e = ELFInfo(lib)
                eclass = e.getElfClass()
                e.Close()
                dbg='Found {0}, using {1}'.format(lib, eclass)
                if myclass == eclass:
                    log.info('%s (== %s)',dbg,myclass)
                    return lib
                log.info('%s (!= %s), skipped',dbg,myclass)
        return givenname

    def getElfClass(self):
        """ Return the ELF Class
        """
        header = self.elf.header
        e_ident = header['e_ident']
        return describe_ei_class(e_ident['EI_CLASS'])

# From http://cgit.gentooexperimental.org/proj/elfix.git/tree/pocs/ldd/ldd.py
def ldpaths(ld_so_conf='/etc/ld.so.conf'):
    """ Generate paths to search for libraries from ld.so.conf.  Recursively
        parse included files.  We assume correct syntax and the ld.so.cache
        is in sync with ld.so.conf.
    """
    with open(ld_so_conf, 'r') as path_file:
        lines = path_file.read()
    lines = re.sub('#.*', '', lines)  # kill comments
    lines = list(re.split(':+|\s+|\t+|\n+|,+', lines))  # man 8 ldconfig

    paths = []
    include_globs = []
    for i in range(0, len(lines)):
        # print('%d: %s' % (i , lines[i]))
        if lines[i] == '':
            continue
        if lines[i] == 'include':
            f = lines[i + 1]
            include_globs.append(f)
            continue
        if lines[i] not in include_globs:
            real_path = os.path.realpath(lines[i])
            if os.path.exists(real_path):
                paths.append(real_path)

    include_files = []
    for g in include_globs:
        if not os.path.isabs(g):
            g = os.path.realpath(os.path.join('/etc/', g))
        include_files += glob.glob(g)
    for c in include_files:
        paths += ldpaths(os.path.realpath(c))

    paths = list(set(paths))
    paths.sort()
    return paths

