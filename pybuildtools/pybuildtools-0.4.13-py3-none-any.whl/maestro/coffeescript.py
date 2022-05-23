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
import codecs
import os
from pathlib import Path
from typing import List, Optional, Union

from tqdm import tqdm

from buildtools import log, os_utils
from buildtools.maestro.base_target import SingleBuildTarget


class CoffeeBuildTarget(SingleBuildTarget):
    BT_TYPE = 'CoffeeScript'
    BT_LABEL = 'COFFEE'

    CHECK_MTIMES = False
    def __init__(self, target: str, files: List[str] = [], dependencies: List[str] = [], coffee_opts: List[str]=['--no-header','-bc'], coffee_executable: Optional[Union[str, Path]]=None, make_map: bool=False, coffee_concat_executable: Optional[Union[str, Path]]=None) -> None:
        if coffee_executable is None:
            coffee_executable = os_utils.which('coffee')
        if coffee_executable is None:
            log.warn('Unable to find coffee on this OS.  Is it in PATH?  Remember to run `yarn global add coffee-script`!')

        if coffee_concat_executable is None:
            coffee_concat_executable = os_utils.which('coffee-concat')
        if coffee_concat_executable is None:
            log.warn('Unable to find coffee-concat on this OS.  Is it in PATH? Remember to run `yarn global add coffee-concat`!')

        self.coffee_executable = coffee_executable
        self.coffee_concat_executable = coffee_concat_executable
        if make_map:
            coffee_opts += ['-M']
        super(CoffeeBuildTarget, self).__init__(target, files, dependencies)
        self.coffee_opts=coffee_opts

    def get_config(self):
        return {
            'opts':                     self.coffee_opts,
            'exec':                     self.coffee_executable,
            'coffee_concat_executable': self.coffee_concat_executable
        }

    def getCoffeeFile(self):
        os_utils.ensureDirExists(os.path.join('tmp', os.path.dirname(self.target)))
        coffeefile = os.path.join('tmp', self.target)
        coffeefile, _ = os.path.splitext(coffeefile)
        coffeefile += '.coffee'
        coffeefile = os.path.abspath(coffeefile)
        return coffeefile

    def getCoffeeMapFile(self):
        os_utils.ensureDirExists(os.path.join('tmp', os.path.dirname(self.target)))
        coffeefile = os.path.join('tmp', self.target)
        coffeefile, _ = os.path.splitext(coffeefile)
        coffeefile += '.yml'
        coffeefile = os.path.abspath(coffeefile)
        return coffeefile

    def clean(self):
        self.removeFile(self.getCoffeeFile()+'.CoffeeBuildTarget.yml')
        self.removeFile(self.getCoffeeMapFile())
        self.removeFile(self.target)

    def build(self):
        os_utils.ensureDirExists(os.path.dirname(self.target))
        # BUGFIX: Coffeescript sometimes doesn't want to overwrite shit. - N3X
        if os.path.isfile(self.target):
            os.remove(self.target)
        coffeefile = self.files[0]
        if len(self.files) > 1:
            coffeefile = self.getCoffeeFile()
            if os.path.isfile(coffeefile):
                os.remove(coffeefile)
            with codecs.open(coffeefile, 'w', encoding='utf-8-sig') as outf:
                tq = tqdm(self.files, desc='Concatenating...', leave=False)
                for infilename in tq:
                    #outf.write('\n`// FILE: {}`\n'.format(infilename))
                    with codecs.open(infilename, 'r', encoding='utf-8-sig') as inf:
                        for line in inf:
                            outf.write(line.rstrip() + "\n")
                    #outf.write('\n`//# sourceURL={}\n`\n'.format(infilename))
                tq.close()
        coffeefile_basename, _ = os.path.splitext(os.path.basename(coffeefile))
        os_utils.cmd([self.coffee_executable] + self.coffee_opts + ['-o', os.path.dirname(self.target), coffeefile], critical=True, echo=self.should_echo_commands(), show_output=True)
        coffee_output_file = os.path.join(os.path.dirname(self.target), coffeefile_basename+'.js')
        if coffee_output_file != self.target:
            log.info('Renaming %s to %s...', coffee_output_file, self.target)
            os.rename(coffee_output_file, self.target)

class JS2CoffeeBuildTarget(SingleBuildTarget):
    BT_TYPE = 'JS2Coffee'
    BT_LABEL = 'JS2COFFEE'
    def __init__(self, target=None, files=[], dependencies=[], j2coffee_opts=['-i', '2'], js2coffee_path=None):
        if js2coffee_path is None:
            js2coffee_path = os_utils.which('js2coffee')
            if js2coffee_path is None:
                log.warn('Unable to find coffee on this OS.  Is it in PATH?  Remember to run `gem install -g js2coffee`!')
        self.js2coffee_path = js2coffee_path
        super(JS2CoffeeBuildTarget, self).__init__(target, files, [os.path.abspath(__file__)]+dependencies)
        self.js2coffee_opts = j2coffee_opts

    def get_config(self):
        return {
            'opts': self.js2coffee_opts,
            'exec': self.js2coffee_path,
        }

    def build(self):
        os_utils.ensureDirExists(os.path.dirname(self.target))
        stdout, stderr = os_utils.cmd_output([self.js2coffee_path]+self.files+self.js2coffee_opts, echo=self.should_echo_commands(), critical=True)
        if stderr.strip() != '':
            log.error(stderr)
        with codecs.open(self.target, 'w', encoding='utf-8-sig') as outf:
            outf.write(stdout)
