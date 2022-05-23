'''
File I/O related buildtargets

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
import re
import shutil
import tqdm
import zipfile

from buildtools import log, os_utils, utils
from buildtools.maestro.base_target import SingleBuildTarget
from buildtools.maestro.utils import callLambda


class CopyFileTarget(SingleBuildTarget):
    BT_TYPE = 'CopyFile'
    BT_LABEL = 'COPY'

    def __init__(self, target=None, filename=None, dependencies=[], verbose=False):
        super(CopyFileTarget, self).__init__(target, [filename], dependencies)
        self.name = f'{filename} -> {target}'

    def build(self):
        os_utils.ensureDirExists(os.path.dirname(self.target), noisy=False)
        os_utils.single_copy(self.files[0], self.target, verbose=False, as_file=True)
        self.touch(self.target)


class MoveFileTarget(SingleBuildTarget):
    BT_TYPE = 'MoveFile'
    BT_LABEL = 'MOVE'

    def __init__(self, target=None, filename=None, dependencies=[]):
        super(MoveFileTarget, self).__init__(target, [filename], dependencies)
        self.name = f'{filename} -> {target}'

    def build(self):
        os_utils.ensureDirExists(os.path.dirname(self.target), noisy=False)
        shutil.move(self.files[0], self.target)


class ReplaceTextTarget(SingleBuildTarget):
    BT_TYPE = 'ReplaceText'
    BT_LABEL = 'REPLACETEXT'

    def __init__(self, target=None, filename=None, replacements=None, dependencies=[], read_encoding='utf-8-sig', write_encoding='utf-8-sig', display_progress=False):
        self.replacements = replacements
        self.subject = filename
        self.read_encoding = read_encoding
        self.write_encoding = write_encoding
        self.display_progress = display_progress
        super().__init__(target, [filename], dependencies)

    def serialize(self):
        dat = super(ReplaceTextTarget, self).serialize()
        dat['replacements'] = self.replacements
        dat['read-encoding'] = self.read_encoding
        dat['write-encoding'] = self.write_encoding
        if self.display_progress:
            dat['display-progress'] = self.display_progress
        return dat

    def deserialize(self, data):
        super(ReplaceTextTarget, self).deserialize(data)
        self.replacements = data['replacements']
        self.read_encoding = data['read-encoding']
        self.write_encoding = data['write-encoding']
        self.display_progress = data.get('display-progress', False)
        self.subject = data['files'][0]

    def get_config(self):
        return {
            'replacements': self.replacements,
            'read-encoding': self.read_encoding,
            'write-encoding': self.write_encoding
        }

    def build(self):
        def process_line(outf, line):
            for needle, replacement in self.replacements.items():
                needle = callLambda(needle)
                # if isinstance(replacement, SerializableLambda):
                #    replacement = replacement()
                line = re.sub(needle, replacement, line)
            outf.write(line)
        os_utils.ensureDirExists(os.path.dirname(self.target))
        nbytes = os.path.getsize(self.subject)
        with codecs.open(self.subject, 'r', encoding=self.read_encoding) as inf:
            with codecs.open(self.target + '.out', 'w', encoding=self.write_encoding) as outf:
                progBar = tqdm.tqdm(total=nbytes, unit='B', leave=False) if self.display_progress else None
                linebuf = ''
                nlines = 0
                nbytes = 0
                lastbytecount = 0
                lastcheck = 0
                longest_line = 0
                while True:
                    block = inf.read(4096)
                    block = block.replace('\r\n', '\n')
                    block = block.replace('\r', '\n')
                    if not block:  # EOF
                        process_line(outf, linebuf)
                        nlines += 1
                        charsInLine = len(linebuf)
                        if charsInLine > longest_line:
                            longest_line = charsInLine
                        break
                    for c in block:
                        nbytes += 1
                        if self.display_progress:
                            # if nbytes % 10 == 1:
                            cms = utils.current_milli_time()
                            if cms - lastcheck >= 250:
                                progBar.set_postfix({'linebuf': len(linebuf), 'nlines': nlines})
                                progBar.update(nbytes - lastbytecount)
                                lastcheck = cms
                                lastbytecount = nbytes
                        linebuf += c
                        if c in '\r\n':
                            process_line(outf, linebuf)
                            nlines += 1
                            charsInLine = len(linebuf)
                            if charsInLine > longest_line:
                                longest_line = charsInLine
                            linebuf = ''
                if self.display_progress:
                    progBar.close()
                    with log.info('Completed.'):
                        log.info('Lines.......: %d', nlines)
                        log.info('Chars.......: %d', nbytes)
                        log.info('Longest line: %d chars', longest_line)
        shutil.move(self.target + '.out', self.target)

class PrependToFileTarget(SingleBuildTarget):
    BT_TYPE = 'Prepend'
    BT_LABEL = 'PREPEND'

    def __init__(self, target, filename, text='', dependencies=[], read_encoding='utf-8-sig', write_encoding='utf-8-sig', display_progress=False):
        self.text = text
        self.subject = filename
        self.read_encoding = read_encoding
        self.write_encoding = write_encoding
        self.display_progress = display_progress
        super().__init__(target, [filename], dependencies)

    def serialize(self):
        dat = super(PrependToFileTarget, self).serialize()
        dat['subject'] = self.subject
        dat['text'] = self.text
        dat['read-encoding'] = self.read_encoding
        dat['write-encoding'] = self.write_encoding
        if self.display_progress:
            dat['display-progress'] = self.display_progress
        return dat

    def deserialize(self, data):
        super(PrependToFileTarget, self).deserialize(data)
        self.subject = data['subject']
        self.text = data['text']
        self.read_encoding = data['read-encoding']
        self.write_encoding = data['write-encoding']
        self.display_progress = data.get('display-progress', False)
        self.subject = data['files'][0]

    def get_config(self):
        return {
            'subject': self.subject,
            'text': self.text,
            'read-encoding': self.read_encoding,
            'write-encoding': self.write_encoding
        }

    def build(self):
        linebuf = ''
        nlines = 0
        lastbytecount = 0
        lastcheck = 0
        longest_line = 0
        os_utils.ensureDirExists(os.path.dirname(self.target))
        nbytes = os.path.getsize(self.subject)
        with codecs.open(self.subject, 'r', encoding=self.read_encoding) as inf:
            with codecs.open(self.target + '.out', 'w', encoding=self.write_encoding) as outf:
                progBar = tqdm.tqdm(total=nbytes, unit='B', leave=False) if self.display_progress else None
                outf.write(self.text)
                while True:
                    block = inf.read(4096)
                    block = block.replace('\r\n', '\n')
                    block = block.replace('\r', '\n')
                    if not block:  # EOF
                        outf.write(linebuf)
                        nlines += 1
                        charsInLine = len(linebuf)
                        if charsInLine > longest_line:
                            longest_line = charsInLine
                        break
                    for c in block:
                        nbytes += 1
                        if self.display_progress:
                            # if nbytes % 10 == 1:
                            cms = utils.current_milli_time()
                            if cms - lastcheck >= 250:
                                progBar.set_postfix({'linebuf': len(linebuf), 'nlines': nlines})
                                progBar.update(nbytes - lastbytecount)
                                lastcheck = cms
                                lastbytecount = nbytes
                        linebuf += c
                        if c in '\r\n':
                            outf.write(linebuf)
                            nlines += 1
                            charsInLine = len(linebuf)
                            if charsInLine > longest_line:
                                longest_line = charsInLine
                            linebuf = ''
                if self.display_progress:
                    progBar.close()
                    with log.info('Completed.'):
                        log.info('Lines.......: %d', nlines)
                        log.info('Chars.......: %d', nbytes)
                        log.info('Longest line: %d chars', longest_line)
        shutil.move(self.target + '.out', self.target)

class ConcatenateBuildTarget(SingleBuildTarget):
    BT_TYPE = 'Concatenate'
    BT_LABEL = 'CONCAT'

    def __init__(self, target, files, dependencies=[], read_encoding='utf-8-sig', write_encoding='utf-8-sig'):
        self.write_encoding = write_encoding
        self.read_encoding = read_encoding
        self.subjects = files
        super(ConcatenateBuildTarget, self).__init__(target, dependencies=dependencies, files=[os.path.abspath(__file__)] + files)

    def serialize(self):
        data = super(ConcatenateBuildTarget, self).serialize()
        if os.path.abspath(__file__) in data['files']:
            data['files'].remove(os.path.abspath(__file__))
        data['encoding'] = {
            'read': self.read_encoding,
            'write': self.write_encoding
        }
        return data

    def deserialize(self, data):
        super(ConcatenateBuildTarget, self).deserialize(data)
        if os.path.abspath(__file__) not in data['files']:
            data['files'].append(os.path.abspath(__file__))
        enc = data.get('encoding', {})
        self.read_encoding = enc.get('read', 'utf-8-sig')
        self.write_encoding = enc.get('write', 'utf-8-sig')

    def get_config(self):
        return {
            'read-encoding': self.read_encoding,
            'write-encoding': self.write_encoding
        }

    def build(self):
        with codecs.open(self.target + '.tmp', 'w', encoding=self.write_encoding) as outf:
            for subj in tqdm.tqdm(self.subjects, leave=False):
                with codecs.open(subj, 'r', encoding=self.read_encoding) as f:
                    outf.write(f.read())
        if os.path.isfile(self.target):
            os.remove(self.target)
        shutil.move(self.target + '.tmp', self.target)


class CopyFilesTarget(SingleBuildTarget):
    BT_TYPE = 'CopyFiles'
    BT_LABEL = 'COPYFILES'

    def __init__(self, target, source, destination, dependencies=[], verbose=False, ignore=None, show_progress=False):
        self.source = source
        self.destination = destination
        self.verbose = verbose
        self.ignore=ignore
        self.provided_files=os_utils.get_file_list(source, start=source, prefix=destination)
        self.show_progress=show_progress
        super(CopyFilesTarget, self).__init__(target, dependencies=dependencies, files=[self.source, self.destination, os.path.abspath(__file__)])
        self.name = f'{source} -> {destination}'

    def is_stale(self):
        return True

    def serialize(self):
        data = super(CopyFilesTarget, self).serialize()
        data['files'] = [self.source, self.destination]
        return data

    def deserialize(self, data):
        super(CopyFilesTarget, self).deserialize(data)
        self.source, self.destination = data['files']

    def provides(self):
        return [self.target]+self.provided_files

    def get_config(self):
        return [self.source, self.destination, self.ignore, self.provided_files]

    def build(self):
        os_utils.copytree(self.source, self.destination, verbose=self.verbose, ignore=self.ignore, progress=self.show_progress)
        self.touch(self.target)

class RSyncRemoteTarget(SingleBuildTarget):
    BT_LABEL = 'RSYNC'

    def __init__(self, sources, destination, rsync_executable=None, progress=False, delete=False, opts=['-Rruavp'], chmod=0o755, chown=None, chgrp=None, show_output=False, dependencies=[], provides=[], name='rsync', keyfile=None):
        self.rsync_executable = rsync_executable or os_utils.which('rsync')
        self.opts = opts
        self.progress = progress
        self.chmod = chmod
        self.chown = chown
        self.chgrp = chgrp
        self.show_output = show_output
        self.progress = progress
        self.sources = sources
        self.delete = delete
        self.destination = destination
        self.keyfile = keyfile
        files = []
        for source in sources:
            with log.info('Scanning %s...', source):
                if os.path.isdir(source):
                    files += os_utils.get_file_list(source)
                if os.path.isfile(source):
                    files += [source]
        super().__init__(target=self.genVirtualTarget(name.replace('\\', '_').replace('/', '_')), files=files, dependencies=dependencies, provides=provides, name=name)

    def is_stale(self):
        return True

    def build(self):
        # call rsync -Rrav --progress *.mp3 root@ss13.nexisonline.net:/host/ss13.nexisonline.net/htdocs/media/
        cmd = [self.rsync_executable]
        cmd += self.opts
        if self.progress:
            cmd += ['--progress']
        if self.delete:
            cmd += ['--delete', '--delete-before']
        if self.chmod != None:
            cmd += [f'--chmod={self.chmod:o}']
        if self.chown != None:
            chown = self.chown
            if self.chgrp is not None:
                chown += ':' + self.chgrp
            cmd += [f'--chown={chown}']
        if self.keyfile != None:
            keypath = self.keyfile
            os_utils.cmd(['chmod','400',keypath], echo=False, show_output=True, critical=True)
            if os_utils.is_windows() and ':' in keypath:
                #keypath = os_utils.cygpath(keypath)
                keypath = keypath.replace('\\','/')
            cmd += ['-e', f"ssh -i {keypath}"]
        cmd += [x.replace('\\', '/') for x in self.sources]
        cmd += [self.destination]

        os_utils.cmd(cmd, show_output=self.show_output, echo=True or self.should_echo_commands(), critical=True, acceptable_exit_codes=[0, 23])
        self.touch(self.target)

class ExtractArchiveTarget(SingleBuildTarget):
    BT_TYPE = 'ExtractArchive'
    BT_LABEL = 'EXTRACT'

    def __init__(self, target_dir: str, archive: str, dependencies=[], provides=[]):
        self.target_dir = target_dir
        self.archive = archive
        super().__init__(target=self.genVirtualTarget(), files=[self.archive, self.target_dir, os.path.abspath(__file__)], dependencies=dependencies, provides=provides)

    def get_config(self):
        return [self.archive, self.target_dir]
    def build(self):
        if self.archive.endswith('.zip'):
            with log.info('Extracting %r as ZIP archive...', self.archive):
                with zipfile.ZipFile(self.archive) as z:
                    z.extractall(path=self.target_dir)
