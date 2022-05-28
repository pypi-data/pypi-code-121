# vim:set ts=4 sw=4 et nowrap syntax=python ff=unix:
#
# Copyright 2020 Mark Crewson <mark@crewson.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import shutil
import tarfile
import zipfile

from jinja2 import Template

from ..download import HttpDownloader
from ..framew.application import OperationError
from ..framew.log import getlog
from ..packlock import PackLock

##############################################################################


# A base class for builders that only performs the packlock loading
# functions. This is separated from the BaseBuilder so for the use
# of cmds the need to read the packlock files, but do not need all
# of the other building functions or parameters.
#
class BaseLockLoader (object):

    default_packmaker_lock = 'packmaker.lock'

    ##########################################################################

    def __init__(self):
        super(BaseLockLoader, self).__init__()
        self.log = getlog()

    ##########################################################################

    def add_cmdline_args(self, parser):
        parser.add_argument('lockfile', nargs='*', default=[BaseLockLoader.default_packmaker_lock],
                            help='modpack lock file')

    ##########################################################################

    def setup_packlocks(self, parsed_args):
        self.packlock_filenames = parsed_args.lockfile
        self.load_packfiles()

    ##########################################################################

    def load_packfiles(self):
        for filename in self.packlock_filenames:
            if not os.path.exists(filename):
                raise OperationError('Cannot find pack lock file: {}'.format(filename))

        self.packlock = PackLock(self.packlock_filenames)
        self.packlock.load()

##############################################################################


class BaseBuilder (BaseLockLoader):

    release_extensions = {'zip': 'zip',
                          'tgz': 'tar.gz',
                          'tbz2': 'tar.bz2',
                          'txz': 'tar.xz'
                          }

    # A sublocation that specific builders will use as their actual build_dir.
    # (for example, the local builder, specified build_subloc = 'local', and
    # then the builder will use the 'build/local' directory as its build location.
    # This allows multiple builders to work within the same build location with
    # out overwriting each others' content.
    build_subloc = None

    default_build_dir = 'build'

    ##########################################################################

    def __init__(self, config):
        super(BaseBuilder, self).__init__()
        self.config = config

    ##########################################################################

    def add_cmdline_args(self, parser):
        super(BaseBuilder, self).add_cmdline_args(parser)
        parser.add_argument('--build-dir', '-b', default=None,
                            help='base directory for build artifacts')
        parser.add_argument('--release-dir', '-r', default=None,
                            help='base directory for release artifacts')
        parser.add_argument('--cache-dir', default=None,
                            help='base directory for cached artifacts')
        parser.add_argument('--release-format', choices=('zip', 'tgz', 'tbz2', 'txz'), default='zip',
                            help='archive format for release package')

    ##########################################################################

    def setup_build(self, parsed_args):
        self.build_dir = parsed_args.build_dir
        if self.build_dir is None:
            self.build_dir = self.config.get('locations::build')
        if self.build_dir is None:
            self.build_dir = self.default_build_dir

        self.release_dir = parsed_args.release_dir
        if self.release_dir is None:
            self.release_dir = self.config.get('locations::release')
        if self.release_dir is None:
            self.release_dir = os.path.join(self.build_dir, 'release')

        self.cache_dir = parsed_args.cache_dir
        if self.cache_dir is None:
            self.cache_dir = self.config.get('locations::cache')
        if self.cache_dir is None:
            self.cache_dir = os.path.join(self.build_dir, 'cache')

        self.release_format = parsed_args.release_format
        self.release_extension = self.release_extensions[self.release_format]

        self.addons_downloader = HttpDownloader(self.cache_location('addons'))

        self.setup_packlocks(parsed_args)

    ##########################################################################

    def do_build(self):
        pass

    ##########################################################################

    def build_location(self, subloc=None):
        loc = self.build_dir
        if self.build_subloc is not None:
            loc = os.path.join(loc, self.build_subloc)
        if subloc is not None:
            loc = os.path.join(loc, subloc)
        if not os.path.exists(loc):
            os.makedirs(loc)
        return loc

    ##########################################################################

    def cache_location(self, subloc=None):
        loc = self.cache_dir
        if subloc is not None:
            loc = os.path.join(loc, subloc)
        if not os.path.exists(loc):
            os.makedirs(loc)
        return loc

    ##########################################################################

    def release_location(self, subloc=None):
        loc = self.release_dir
        if subloc is not None:
            loc = os.path.join(loc, subloc)
        if not os.path.exists(loc):
            os.makedirs(loc)
        return loc

    ##########################################################################

    def copy_files(self, dest=None, files_iterator=None):
        if dest is None:
            dest = self.build_location()
        if files_iterator is None:
            files_iterator = self.packlock.files
        for files in files_iterator:
            location = files['location']
            if not os.path.exists(location):
                self.log.warn('Skipping files, cannot find location: {}'.format(location))
                continue
            if not os.path.isdir(location):
                self.log.warn('Skipping files, location is not a directory: {}'.format(location))
                continue
            self.__copy_tree(files['location'], dest, files.get('template', False))

    ##########################################################################

    def copy_addon(self, dest, mod):
        def copy_file(url, temp):
            localfile = os.path.join(dest, os.path.basename(temp))
            shutil.copy2(temp, localfile)

        self.addons_downloader.add_download(mod.downloadUrl, mod.fileName)
        self.addons_downloader.run(post=copy_file)

    ##########################################################################

    def copy_mods(self, dest, mod_iterator=None):
        def copy_file(url, temp):
            localfile = os.path.join(dest, os.path.basename(temp))
            shutil.copy2(temp, localfile)

        if mod_iterator is None:
            mod_iterator = self.packlock.get_all_mods()
        for mod in mod_iterator:
            self.addons_downloader.add_download(mod.downloadUrl, mod.fileName)
        self.addons_downloader.run(post=copy_file)

    ##########################################################################

    def copy_resourcepacks(self, dest, rep_iterator=None):
        def copy_file(url, temp):
            localfile = os.path.join(dest, os.path.basename(temp))
            shutil.copy2(temp, localfile)

        if rep_iterator is None:
            rep_iterator = self.packlock.get_all_resourcepacks()
        for rep in rep_iterator:
            self.addons_downloader.add_download(rep.downloadUrl, rep.fileName)
        self.addons_downloader.run(post=copy_file)

    ##########################################################################

    def download_mods(self, mod_iterator=None):
        self.log.debug('Downloading mods ...')
        if mod_iterator is None:
            mod_iterator = self.packlock.get_all_mods()
        for mod in mod_iterator:
            self.addons_downloader.add_download(mod.downloadUrl, mod.fileName)
        self.addons_downloader.run()

    ##########################################################################

    def download_resourcepacks(self, rep_iterator=None):
        self.log.debug('Downloading resourcepacks ...')
        if rep_iterator is None:
            rep_iterator = self.packlock.get_all_resourcepacks()
        for rep in rep_iterator:
            self.addons_downloader.add_download(rep.downloadUrl, rep.fileName)
        self.addons_downloader.run()

    ##########################################################################

    def release_pkg(self, dest, source=None, format=None):
        if source is None:
            source = self.build_location()
        if format is None:
            format = self.release_format
        if format == 'zip':
            self.__zip_tree(source, dest)
        elif format == 'tgz':
            self.__tar_tree(source, dest, compression='gz')
        elif format == 'tbz2':
            self.__tar_tree(source, dest, compression='bz2')
        elif format == 'txz':
            self.__tar_tree(source, dest, compression='xz')
        else:
            raise OperationError('Unknown release format: {}'.format(self.release_format))

    ##########################################################################

    def __copy_tree(self, source, dest, template=False):
        names = os.listdir(source)
        if not os.path.exists(dest):
            os.makedirs(dest)
        for name in names:
            srcname = os.path.join(source, name)
            dstname = os.path.join(dest, name)
            try:
                if os.path.isdir(srcname):
                    self.__copy_tree(srcname, dstname, template)
                else:
                    if template:
                        self.__copy_template(srcname, dstname)
                    else:
                        shutil.copy2(srcname, dstname)
            except OSError:
                raise

    def __copy_template(self, srcname, dstname):
        with open(srcname, 'r') as src:
            templ = Template(src.read())
            out = templ.render(self.packlock.get_all_metadata())
            with open(dstname, 'w') as dst:
                dst.write(out)

    ##########################################################################

    @staticmethod
    def __zip_tree(source, dest):
        with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source):
                for file in files:
                    # bad attempt at preventing the zipfile from including itself
                    if file == os.path.basename(dest):
                        continue
                    zipf.write(os.path.join(root, file),
                               os.path.join(root[len(source):], file))

    @staticmethod
    def __tar_tree(source, dest, compression='gz'):
        with tarfile.open(dest, 'w:{}'.format(compression)) as tarf:
            for root, dirs, files in os.walk(source):
                for file in files:
                    # bad attempt at preventing the tarfile from including itself
                    if file == os.path.basename(dest):
                        continue
                    tarf.add(os.path.join(root, file),
                             os.path.join(root[len(source):], file))

##############################################################################
# THE END
