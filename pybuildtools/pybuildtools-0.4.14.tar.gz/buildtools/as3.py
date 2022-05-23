'''
ActionScript3-related shit

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
import re
from pathlib import Path
from typing import Container, Iterable, Mapping, Set, Union

from .indentation import getIndentChars

_REG_IMPORT_STOP_A = re.compile(r'(public|private) (class|function)')
_REG_IMPORT_STOP_B = re.compile(r'/\*\*')
_REG_IMPORT = re.compile(r'import ([a-zA-Z0-9_\.\*]+);')

def calculateNewImports(readImports: Container[str], requiredImports: Iterable[str]) -> Set[str]:
    # print(repr(readImports))
    newImports = set()
    for imp in requiredImports:
        chunks = imp.split('.')
        chunks[-1] = '*'
        genimport = '.'.join(chunks)
        if genimport in readImports or imp in readImports:
            continue
        else:
            newImports.add(imp)
    return newImports


def ensureConditionalImports(filename: Union[str, Path], matchToImports: Mapping[str, Iterable[str]], sort: bool=False) -> None:
    requires = set()
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            for match, imports in matchToImports.items():
                if re.search(match, line) is not None:
                    requires |= set([i for i in imports if i not in requires])
    if len(requires) > 0:
        ensureImportsExist(filename, requires, sort=sort)


def _reg_matches(line, regex, action=None):
    m = regex.search(line)
    if m is not None:
        if action is not None:
            action(line, m)
        return True
    return False

def ensureImportsExist(filename: Union[str, Path], requiredImports: Iterable[str], sort: bool=False) -> None:
    readImports: Set[str] = set()
    subject: Path = Path(filename)
    subject_tmp: Path = subject.with_suffix(subject.suffix+'.tmp')
    with subject.open('r') as f:
        with subject_tmp.open('w') as w:
            ln = 0
            #lastIndent = ''
            writingImports = True
            for line in f:
                ln += 1
                oline = line
                currentLine = line.lstrip().strip('\r\n')
                indent = getIndentChars(oline)
                line = line.strip()
                if writingImports:
                    m = _REG_IMPORT.search(line)
                    if m is not None:
                        readImports.add(m.group(1))
                        #lastIndent = indent
                        if sort:
                            continue
                    if _reg_matches(line, _REG_IMPORT_STOP_A) or _reg_matches(line, _REG_IMPORT_STOP_B):
                        added = calculateNewImports(readImports, requiredImports)
                        if sort:
                            added |= readImports
                        if added:
                            for newImport in sorted(added):
                                w.write(f'{indent}import {newImport};\n')
                            w.write('\n')
                        writingImports = False
                w.write(indent + currentLine + '\n')
    os.replace(subject_tmp, subject)
