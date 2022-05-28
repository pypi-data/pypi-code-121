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

import hashlib
import json
import os.path

from .base import BaseBuilder

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution('packmaker').version
except Exception:
    __version__ = 'unknown'

##############################################################################


class PackBuilder (BaseBuilder):

    build_subloc = 'pack'

    pack_version = '1'

    ##########################################################################

    def do_build(self):
        self.log.info('Generating metadata file ...')
        self.make_metadata()

        self.log.info('Generating manifest file ...')
        self.make_manifest()

        self.log.info('Copying local files ...')
        self.copy_files(self.build_location('files'), self.packlock.yield_clientonly_files())

        # add the packmaker "filemarker" file
        with open(os.path.join(self.build_location(), 'packmaker.json'), 'w') as pm:
            pm.write(json.dumps({'packmaker': __version__, 'format_version': self.pack_version}))

        pkgfilename = '{}/{}-{}.{}'.format(self.release_location(),
                                           self.packlock.get_metadata('name'),
                                           self.packlock.get_metadata('version'),
                                           'pack')
        self.log.info('Packaging the modpack: {} ...'.format(pkgfilename))
        self.release_pkg(pkgfilename, format='tbz2')

    def make_metadata(self):
        metadata = {}
        for k, v in self.packlock.get_all_metadata().items():
            if k not in ('minecraft_version', 'forge_version', 'fabric_version'):
                metadata[k] = v

        with open(os.path.join(self.build_location(), 'metadata.json'), 'w') as mf:
            mf.write(json.dumps(metadata))

    def make_manifest(self):

        #####

        def add_to_mod_manifest(url, filename):
            sha1hash = self.calc_sha1(filename)
            mod_manifest = {'type': 'url',
                            'destination': 'mods/{}'.format(filename),
                            'location': url,
                            'hash': sha1hash,
                            'size': os.path.getsize(filename)
                            }
            manifest['mods'].append(mod_manifest)

        #####

        def add_to_rp_manifest(url, filename):
            sha1hash = self.calc_sha1(filename)
            rp_manifest = {'type': 'url',
                           'destination': 'resourcepacks/{}'.format(filename),
                           'location': url,
                           'hash': sha1hash,
                           'size': os.path.getsize(filename)
                           }
            manifest['resourcepacks'].append(rp_manifest)

        #####

        manifest = {'minecraft': {'version': self.packlock.get_metadata('minecraft_version'),
                                  'modloaders': []
                                  },
                    'mods': [],
                    'resourcepacks': []
                    }

        forge_version = self.packlock.get_metadata('forge_version')
        if forge_version is not None:
            manifest['minecraft']['modloaders'].append({'id': 'forge', 'version': forge_version})

        fabric_version = self.packlock.get_metadata('fabric_version')
        if fabric_version is not None:
            manifest['minecraft']['modloaders'].append({'id': 'fabric', 'version': fabric_version})

        for mod in self.packlock.yield_clientonly_mods():
            self.addons_downloader.add_download(mod.downloadUrl, mod.fileName)
        self.addons_downloader.run(post=add_to_mod_manifest)

        for rp in self.packlock.get_all_resourcepacks():
            self.addons_downloader.add_download(rp.downloadUrl, rp.fileName)
        self.addons_downloader.run(post=add_to_rp_manifest)

        with open(os.path.join(self.build_location(), 'manifest.json'), 'w') as mf:
            mf.write(json.dumps(manifest))

    def calc_sha1(self, filename):
        h = hashlib.sha1()
        with open(filename, 'rb') as hf:
            data = hf.read(65536)
            while data:
                h.update(data)
                data = hf.read(65536)
        return h.hexdigest()


##############################################################################
# THE END
