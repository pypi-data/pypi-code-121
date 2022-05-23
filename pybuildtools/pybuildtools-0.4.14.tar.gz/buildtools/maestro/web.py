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
import re
import json
import enum
import requests
import hashlib
from urllib.request import urlparse
from buildtools import log, os_utils, utils, http
from buildtools.maestro.base_target import SingleBuildTarget

REG_SCSS_IMPORT = re.compile(r"@import '([^']+)';")
class _BaseSCSSBuildTarget(SingleBuildTarget):
    def __init__(self, target=None, files=[], dependencies=[], import_paths=[], output_style='compact', sass_path=None, imported=[]):
        super().__init__(target, files, dependencies)

        #self.compass = compass
        self.import_paths = import_paths
        self.output_style = output_style
        self.imported = imported
        self.sass_path = sass_path

    def getFilesToCompare(self):
        o = super().getFilesToCompare()+self.imported
        for filename in self.files:
            o += self.detectFilesImportedBy(filename)
        return list(set(o))

    def detectFilesImportedBy(self, filename):
        imports=[]
        DIR_CONTEXT = os.path.abspath(os.path.dirname(filename))
        with open(filename, 'r') as f:
            for line in f:
                line=line.strip()
                m = REG_SCSS_IMPORT.match(line)
                if m is not None:
                    for context in [DIR_CONTEXT]+self.import_paths:
                        unprefixed_filename = os.path.join(context, m.group(1))
                        dirname = os.path.dirname(unprefixed_filename)
                        prefixed_basename = '_'+os.path.basename(unprefixed_filename)+'.scss'
                        prefixed_filename = os.path.join(dirname, prefixed_basename)
                        if os.path.isfile(prefixed_filename):
                            imports += [prefixed_filename]
                            imports += self.detectFilesImportedBy(prefixed_filename)
                            break
        if len(imports)==0:
            log.debug('%s imported 0 files.', filename)
        else:
            with log.debug('%s imported %d files:', filename, len(imports)):
                for i in imports:
                    log.debug(i)
        return imports

    def serialize(self):
        dat = super().serialize()
        #dat['compass'] = self.compass
        dat['imports'] = self.import_paths
        dat['style'] = self.output_style
        dat['imported'] = self.imported
        return dat

    def deserialize(self, data):
        super().deserialize(data)
        #self.compass = data.get('compass', False)
        self.import_paths = data.get('imports', [])
        self.output_style = data.get('style', 'compact')
        self.imported = data.get('imported', [])

    def get_config(self):
        return {
            'import-paths': self.import_paths,
            'output-style': self.output_style,
            'imported': self.imported
        }

class DartSCSSBuildTarget(_BaseSCSSBuildTarget):
    BT_TYPE = 'DART-SCSS'
    BT_LABEL = 'DART SCSS'

    def __init__(self, target=None, files=[], dependencies=[], import_paths=[], output_style='expanded', sass_path=None, imported=[], source_map=None):
        self.source_map = source_map
        if self.source_map is None:
            self.source_map = output_style == 'expanded'
        if sass_path is None:
            sass_path = os_utils.which('sass')
            if sass_path is None:
                log.warn('Unable to find sass on this OS.  Is it in PATH?  Remember to run `npm install -g sass`!')
        super().__init__(target, files, dependencies, import_paths=import_paths, output_style=output_style, sass_path=sass_path, imported=imported)

    def build(self):
        sass_cmd = []

        sass_cmd = [self.sass_path]
        args = ['--no-color', '-q', '--stop-on-error', '-s', self.output_style]
        if self.source_map:
            args += ['--embed-sources', '--embed-source-map']
        for import_path in self.import_paths:
            args += ['-I', import_path]

        #os_utils.ensureDirExists(os.path.join('tmp', os.path.dirname(self.target)))
        os_utils.ensureDirExists(os.path.dirname(self.target))
        os_utils.cmd(sass_cmd + args + self.files + [self.target], critical=True, echo=self.should_echo_commands(), show_output=True)

class RubySCSSBuildTarget(_BaseSCSSBuildTarget):
    BT_TYPE = 'RUBY-SCSS'
    BT_LABEL = 'RUBY SCSS'

    def __init__(self, target=None, files=[], dependencies=[], compass=False, import_paths=[], output_style='compact', sass_path=None, imported=[]):
        if sass_path is None:
            sass_path = os_utils.which('sass')
            if sass_path is None:
                log.warn('Unable to find sass on this OS.  Is it in PATH?  Remember to run `gem install sass compass`!')
        super().__init__(target, files, dependencies, import_paths=import_paths, output_style=output_style, sass_path=sass_path, imported=imported)
        self.compass = compass

    def getFilesToCompare(self):
        return super().getFilesToCompare()+self.imported

    def serialize(self):
        dat = super().serialize()
        dat['compass'] = self.compass
        return dat

    def deserialize(self, data):
        super().deserialize(data)
        self.compass = data.get('compass', False)

    def get_config(self):
        data = super().get_config()
        data['compass'] = self.compass
        return data

    def build(self):
        sass_cmd = []

        if self.sass_path.endswith('.bat') or self.sass_path.endswith('.BAT'):
            RUBYDIR = os.path.dirname(self.sass_path)
            sass_cmd = [os.path.join(RUBYDIR, 'ruby.exe'),
                        os.path.join(RUBYDIR, 'sass')]
        else:
            sass_cmd = [self.sass_path]
        args = ['--scss', '--force', '-C', '-t', self.output_style]
        if self.compass:
            args += ['--compass']
        for import_path in self.import_paths:
            args += ['-I=' + import_path]

        #os_utils.ensureDirExists(os.path.join('tmp', os.path.dirname(self.target)))
        os_utils.ensureDirExists(os.path.dirname(self.target))
        os_utils.cmd(sass_cmd + args + self.files + [self.target], critical=True, echo=self.should_echo_commands(), show_output=True)


class SCSSConvertTarget(SingleBuildTarget):
    BT_TYPE = 'SCSSConvert'
    BT_LABEL = 'SCSSCONVERT'

    def __init__(self, target=None, files=[], dependencies=[], sass_convert_path=None):
        super(SCSSConvertTarget, self).__init__(target, files, dependencies)
        if sass_convert_path is None:
            sass_convert_path = os_utils.which('sass-convert')
            if sass_convert_path is None:
                log.warn('Unable to find sass-convert on this OS.  Is it in PATH?  Remember to run `gem install sass compass`!')
        self.sass_convert_path = sass_convert_path

    def get_config(self):
        return [self.sass_convert_path]

    def build(self):
        sass_cmd = []
        if self.sass_convert_path.endswith('.bat') or self.sass_convert_path.endswith('.BAT'):
            RUBYDIR = os.path.dirname(self.sass_convert_path)
            sass_cmd = [os.path.join(RUBYDIR, 'ruby.exe'), os.path.join(RUBYDIR, 'sass-convert')]
        else:
            sass_cmd = [self.sass_convert_path]
        args = ['-F', 'css', '-T', 'scss', '-C']
        #os_utils.ensureDirExists(os.path.join('tmp', os.path.dirname(self.target)))
        os_utils.ensureDirExists(os.path.dirname(self.target))
        os_utils.cmd(sass_cmd + args + self.files + [self.target], critical=True, echo=self.should_echo_commands(), show_output=True)


class SVG2PNGBuildTarget(SingleBuildTarget):
    BT_TYPE = 'SVG2PNG'
    BT_LABEL = 'SVG2PNG'

    def __init__(self, target, inputfile, height, width, dependencies=[], inkscape=None):
        self.height = height
        self.width = width

        self.inkscape = inkscape
        if self.inkscape is None:
            # Last-ditch for Windows.
            self.inkscape = os_utils.which('inkscape') or 'C:\\Program Files\\Inkscape\\inkscape.exe'

        super(SVG2PNGBuildTarget, self).__init__(target, files=[inputfile], dependencies=dependencies)

    def get_config(self):
        return {'height': self.height, 'width': self.width, 'path': self.inkscape}

    def build(self):
        os_utils.ensureDirExists(os.path.dirname(self.target))
        os_utils.cmd([self.inkscape, '-z', '-e', self.target, '-h', str(self.height), '-w', str(self.width), self.files[0]], critical=True, echo=self.should_echo_commands(), show_output=True)


class ICOBuildTarget(SingleBuildTarget):
    BT_TYPE = 'ICO'
    BT_LABEL = 'ICO'

    def __init__(self, target, inputfiles, dependencies=[], convert_executable=None):
        self.convert_executable = convert_executable
        if self.convert_executable is None:
            self.convert_executable = os_utils.which('convert')
        super(ICOBuildTarget, self).__init__(target, files=inputfiles, dependencies=dependencies)

    def get_config(self):
        return {'path': self.convert_executable}

    def build(self):
        os_utils.ensureDirExists(os.path.dirname(self.target))
        command_line = [self.convert_executable]
        command_line += [os.path.relpath(x, os.getcwd()) for x in self.files]
        command_line += [os.path.relpath(self.target, os.getcwd())]
        os_utils.cmd(command_line, critical=True, echo=self.should_echo_commands(), show_output=True)


class UglifyJSTarget(SingleBuildTarget):
    BT_TYPE = 'UglifyJS'
    BT_LABEL = 'UGLIFYJS'

    def __init__(self, target, inputfile, dependencies=[], compress=True, mangle=True, options=[], compress_opts=[], mangle_opts=[], uglify_executable=None):
        self.uglifyjs_executable = uglify_executable
        if self.uglifyjs_executable is None:
            self.uglifyjs_executable = os_utils.which('uglifyjs')

        self.options = []
        if compress:
            self.options += ['-c'] + compress_opts
        if mangle:
            self.options += ['-m'] + mangle_opts

        self.options += options
        super(UglifyJSTarget, self).__init__(target, files=[inputfile], dependencies=dependencies)

    def get_config(self):
        return {'path': self.uglifyjs_executable, 'opts':self.options}

    def build(self):
        cmdline = [self.uglifyjs_executable] + self.options + ['-o', self.target, self.files[0]]
        os_utils.ensureDirExists(os.path.dirname(self.target))
        os_utils.cmd(cmdline, critical=True, echo=self.should_echo_commands())


class MinifySVGTarget(SingleBuildTarget):
    BT_TYPE = 'MinifySVG'
    BT_LABEL = 'SVGO'

    def __init__(self, target, source, dependencies=[], svgo_opts=['-q'], svgo_executable=None):
        self.source = source
        self.svgo_opts = svgo_opts
        self.svgo_cmd = os_utils.which('svgo')
        if svgo_executable is not None:
            self.svgo_cmd = svgo_executable
        if self.svgo_cmd is None:
            log.warn('Unable to find svgo on this OS.  Is it in PATH?  Remember to run `npm install -g svgo`!')

        super(MinifySVGTarget, self).__init__(target, dependencies=dependencies, files=[
            self.source, os.path.abspath(__file__)])

    def build(self):
        os_utils.ensureDirExists(os.path.dirname(self.target))
        os_utils.cmd([self.svgo_cmd, '-i', self.source, '-o', self.target] + self.svgo_opts, echo=self.should_echo_commands(), show_output=True, critical=True)


REG_IMAGEURL = re.compile(r'url\("([^"]+)"\)')
def convert_imgurls_to_dataurls(infile, outfile, basedir):
    def _convert_img2data(m):
        # log.info(m.group(0))
        url = m.group(1)
        if url.startswith('data:'):
            return m.group(0)
        return 'url("{}")'.format(utils.img2blob(os.path.join(basedir, url)).strip())
    with codecs.open(infile, 'r') as inf:
        with codecs.open(outfile, 'w') as outf:
            for line in inf:
                outf.write(REG_IMAGEURL.sub(_convert_img2data, line))


class DatafyImagesTarget(SingleBuildTarget):
    BT_TYPE = 'DatafyImages'
    BT_LABEL = 'DATAFYIMAGES'

    def __init__(self, target, infile, basedir, dependencies=[]):
        self.infile = infile
        self.basedir = basedir
        super().__init__(target, dependencies=dependencies, files=[infile, os.path.abspath(__file__)])

    def build(self):
        convert_imgurls_to_dataurls(self.infile, self.target, self.basedir)

class EBashLayoutFlags(enum.IntFlag):
    PREFIX   = 1
    NAME     = 2
    HASHDIR  = 4
    HIDENAME = 8

class CacheBashifyFiles(SingleBuildTarget):
    BT_TYPE = 'CacheBashify'
    BT_LABEL = 'CACHE BASH'

    CHECK_MTIMES = False

    def __init__(self, destdir, source, manifest, basedirsrc='.', basedirdest=None, dependencies=[], flags=None):
        self.source      = source
        self.destdir     = destdir
        self.basedirsrc  = basedirsrc
        self.basedirdest = basedirdest
        self.manifest    = manifest
        self.flags       = flags if flags is not None else (EBashLayoutFlags.PREFIX|EBashLayoutFlags.NAME)
        target = self.genVirtualTarget(self.source.replace(os.sep, '_').replace('.','_'))
        super().__init__(target=target, dependencies=dependencies, files=[source, os.path.abspath(__file__)])

    def get_config(self):
        return {
            'source': self.source,
            'destdir': self.destdir,
            'basedirsrc': self.basedirsrc,
            'basedirdest': self.basedirdest,
            'manifest': self.manifest,
        }

    def clean(self):
        manifest_data={}
        if os.path.isfile(self.manifest):
            with open(self.manifest, 'r') as f:
                manifest_data = json.load(f)
            for dest in manifest_data.values():
                self.removeFile(dest)
            self.removeFile(self.manifest)
        super().clean()

    def calcFilename(self):
        srchash = utils.md5sum(self.source)
        sourcefilerel = os.path.relpath(self.source, self.basedirsrc)
        dirname = os.path.dirname(sourcefilerel)
        basename, ext = os.path.splitext(os.path.basename(sourcefilerel))
        if basename.endswith('.min'):
            basename=basename[:-4]
            ext = f'.min{ext}'

        newbnparts = []
        if self.basedirdest is not None:
            if (self.flags & EBashLayoutFlags.PREFIX) == EBashLayoutFlags.PREFIX:
                newbnparts += dirname.replace(os.sep, '_').replace('.', '_').split('_')
        if (self.flags & EBashLayoutFlags.NAME) == EBashLayoutFlags.NAME:
            newbnparts += basename.replace(os.sep, '_').replace('.', '_').split('_')
        basename = '_'.join([x for x in newbnparts if x != ''])
        basedestdir = self.basedirdest or dirname
        if (self.flags & EBashLayoutFlags.HASHDIR) == EBashLayoutFlags.HASHDIR:
            a = srchash[0:2]
            b = srchash[2:4]
            basedestdir = os.path.join(basedestdir, a, b)
            srchash = srchash[4:]
        if (self.flags & EBashLayoutFlags.HIDENAME) == EBashLayoutFlags.HIDENAME:
            outfile = os.path.join(basedestdir, f'{srchash}{ext}')
        else:
            outfile = os.path.join(basedestdir, f'{basename}-{srchash}{ext}')
        absoutfile = os.path.join(self.destdir, outfile)
        return sourcefilerel, os.path.relpath(absoutfile, self.destdir), os.path.abspath(absoutfile)

    def get_displayed_name(self):
        relfilename = self.target
        if os.path.isfile(self.source):
            _, relfilename, _ = self.calcFilename()
        return relfilename

    def provides(self):
        o = super().provides()
        #o += [self.manifest]
        if os.path.isfile(self.source):
            o += [self.get_displayed_name()]
        return o

    def is_stale(self):
        '''
        sourcefilerel, reloutfile, absoutfile = self.calcFilename()
        #print(absoutfile)
        #return not os.path.isfile(absoutfile)
        if os.path.join(absoutfile) and os.path.isfile(self.manifest):
            if os.path.isfile(self.manifest):
                with open(self.manifest, 'r') as f:
                    manifest_data = json.load(f)

            sourcefilerel = sourcefilerel.replace(os.sep, '/')
            outfile = reloutfile.replace(os.sep, '/')
            manifest_data[sourcefilerel] = outfile
            with open(self.manifest, 'w') as f:
                json.dump(manifest_data, f, indent=2)
            return False
        '''
        return True

    def build(self):
        sourcefilerel, reloutfile, absoutfile = self.calcFilename()

        sourcefilerel = sourcefilerel.replace(os.sep, '/')
        outfile = reloutfile.replace(os.sep, '/')

        manifest_data={
            sourcefilerel: outfile
        }
        if os.path.isfile(self.manifest):
            with open(self.manifest, 'r') as f:
                manifest_data = json.load(f)

        if sourcefilerel in manifest_data.keys():
            oldfilename = os.path.normpath(os.path.join(self.destdir, manifest_data[sourcefilerel]))
            #log.info(oldfilename)
            #log.info(absoutfile)
            if oldfilename != absoutfile:
                self.removeFile(oldfilename)

        os_utils.ensureDirExists(os.path.dirname(absoutfile), noisy=True)
        os_utils.single_copy(self.source, absoutfile, verbose=False)

        manifest_data[sourcefilerel] = outfile

        os_utils.ensureDirExists(os.path.dirname(self.manifest), noisy=True)
        #print(self.manifest)
        with open(self.manifest, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        self.touch(absoutfile)
        self.touch(self.target)

class DownloadFileTarget(SingleBuildTarget):
    BT_TYPE = 'DownloadFile'
    BT_LABEL = 'DOWNLOAD'

    def __init__(self, target, url, dependencies=[], cache=True):
        self.url = url
        self.urlchunks = urlparse(url)
        self.cache: bool = cache

        self.cache_dir: str = ''
        self.fileid: str = ''
        self.etagdir: str = ''
        self.old_uri_id: str = ''
        self.uri_id: str = ''
        self.cached_dl: str = ''
        self.etagfile: str = ''
        super().__init__(target, dependencies=dependencies, files=[url, os.path.abspath(__file__)])


    def get_displayed_name(self):
        return '{} -> {}'.format(self.url, self.target)

    def _updateCacheInfo(self) -> str:
        self.cache_dir = os.path.join(self.maestro.builddir, 'DownloadFileTarget.cache')

        fileid = hashlib.md5(self.urlchunks.path.encode('utf-8')).hexdigest()

        self.etagdir = os.path.join(self.cache_dir, self.urlchunks.hostname, fileid[0:2], fileid[2:4])
        #self.old_uri_id = hashlib.sha256(self.urlchunks.path.encode('utf-8')).hexdigest()+'.etags'
        uri_id = fileid[4:]+'.etags'
        self.cached_dl = os.path.join(self.etagdir, fileid[4:]+'.dat')

        #if os.path.isfile(os.path.join(etagdir, old_uri_id)):
        #    shutil.move(os.path.join(etagdir, old_uri_id), os.path.join(etagdir, uri_id))

        self.etagfile = os.path.join(self.etagdir, uri_id)

        os_utils.ensureDirExists(self.etagdir)

    def is_stale(self):
        self._updateCacheInfo()
        if not os.path.isfile(self.target):
            return True

        etag = ''
        if os.path.isfile(self.etagfile):
            with open(self.etagfile, 'r') as f:
                etag = f.read()
        with log.info('Checking for changes to %s...', self.url):
            res = requests.head(self.url, allow_redirects=True, headers={'If-None-Match':etag})
            if res.status_code == 304:
                log.info('304 - Not Modified')
                return False
            if etag == res.headers.get('ETag'):
                return False
            res.raise_for_status()
            with log.info('Response headers:'):
                for k, v in res.headers.items():
                    log.info('%s: %s', k, v)
            log.info('HTTP %d', res.status_code)
            with open(self.etagfile, 'w') as f:
                f.write(res.headers.get('ETag'))
        return True

    def build(self):
        os_utils.ensureDirExists(os.path.dirname(self.cached_dl))
        http.DownloadFile(self.url, self.cached_dl, log_after=True, print_status=True, log_before=True)
        os_utils.ensureDirExists(os.path.dirname(self.target))
        os_utils.single_copy(self.cached_dl, self.target, as_file=True, verbose=True)
        if not self.cache:
            os.remove(self.cached_dl)

import os
from buildtools import os_utils
from buildtools.maestro.base_target import SingleBuildTarget


class WebifyTarget(SingleBuildTarget):
    BT_TYPE = 'Webify'
    BT_LABEL = 'Webify'

    def __init__(self, destination, source, dependencies=[], webify_base_path='bin/', webify_win32='webify-win-32.exe', webify_linux='webify-linux-x86_64'):
        executable = webify_win32 if os_utils.is_windows() else webify_linux
        self.webify = os.path.abspath(os.path.join(webify_base_path, executable))
        self.source = source
        self.destination = destination
        destbasename, _ = os.path.splitext(self.destination)
        _, srcext = os.path.splitext(self.source)
        self.intermediate_filename = destbasename + '.' + (srcext.strip('.'))
        super().__init__(destination, dependencies=dependencies, files=[os.path.abspath(__file__), self.source, self.webify])

    def get_config(self):
        return {
            'source': self.source,
            'dest': self.destination,
            'webify': self.webify,
            'intermediate_filename': self.intermediate_filename,
        }

    def provides(self):
        base,_ = os.path.splitext(self.intermediate_filename)
        o=[]
        for ext in ['eot', 'woff', 'ttf', 'svg']:
            o += [base + '.' + ext]
        return o

    def build(self):
        os_utils.ensureDirExists(os.path.dirname(self.destination), noisy=True)
        os_utils.single_copy(self.source, self.intermediate_filename, verbose=True)
        os_utils.cmd([self.webify, self.intermediate_filename], echo=True, critical=True)
