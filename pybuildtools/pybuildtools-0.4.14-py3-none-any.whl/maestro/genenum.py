'''
Enum generators for various languages.

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
from pathlib import Path
from typing import List, Union

from buildtools import log, os_utils
from buildtools.maestro.base_target import SingleBuildTarget


from buildtools.maestro.enumwriters.enumwriter import EnumWriter


from buildtools.maestro.enumwriters.types import EnumDefinition

from ruamel.yaml import YAML  # isort: skip
yaml = YAML(typ='safe', pure=True)


class GenerateEnumTarget(SingleBuildTarget):
    BT_LABEL = 'ENUM'

    def __init__(self, target: Union[str, Path], source: Union[str, Path], writer: EnumWriter, dependencies: List[str] = []) -> None:
        self.filename: Path = Path(source)
        self.outfile: Path = Path(target)
        self.writer: EnumWriter = writer
        self.writer.parent = self
        super().__init__(str(target), [
            str(self.filename)], dependencies, name=str(self.filename))

    def build(self):
        data = {}
        with open(self.filename, 'r') as r:
            data = yaml.load(r)['enum']

        ed = EnumDefinition()
        ed.deserialize(data)
        if ed.tests:
            ed.tests.test(ed)
        os_utils.ensureDirExists(os.path.dirname(self.target), noisy=True)
        with open(self.target, 'w') as w:
            self.writer.write(w, ed)
