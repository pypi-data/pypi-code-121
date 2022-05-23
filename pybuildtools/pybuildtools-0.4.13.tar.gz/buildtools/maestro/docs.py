'''
BLURB GOES HERE.

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
from typing import List
from .base_target import BuildTarget, SingleBuildTarget
from .. import os_utils

class RonnBuildTarget(BuildTarget):
    BT_LABEL = 'RONN'
    def __init__(self, markdown_filename, section:int=1, dependencies: List[str]=[], ronn_executable: str=None):
        self.markdown_filename: str = markdown_filename
        self.section: int = section
        self.dependencies: List[str] = dependencies
        self.ronn_executable: str = ronn_executable or os_utils.which('ronn')

        self.parent_dir: str = os.path.dirname(self.markdown_filename)
        basename, _ = os.path.splitext(os.path.basename(self.markdown_filename))
        self.roff_filename: str = os.path.join(self.parent_dir, f'{basename}')
        self.html_filename: str = os.path.join(self.parent_dir, f'{basename}.html')
        super().__init__(targets=[self.roff_filename, self.html_filename], files=[markdown_filename], dependencies=dependencies)

    def build(self):
        os_utils.cmd([self.ronn_executable, self.markdown_filename], echo=self.should_echo_commands(), show_output=False)
