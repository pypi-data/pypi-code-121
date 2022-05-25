"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

import os

from typing import Any, Dict, List, Union

PathLike = Union[os.PathLike, str]
# not a perfect JSON definition but no need for too fancy, it is mostly for documentation
# see https://stackoverflow.com/a/51294709
JsonDict = Dict[str, Any]

# TODO: Do a proper cleanup for custom types
#  Either start using TypedDicts after Alpine releases Python 3.8 or start using proper classes

# file paths following nested archives with left one being the toplevel archive/file path
FullPath = List[str]
# same as above but also states the archive/file type for each path
ExtendedFullPath = List[Dict[str, str]]

WhiteoutEntry = JsonDict
# WhiteoutEntry example:
# {
#     'object': '.wh.libformw.so.6',
#     'fullpath': ['bash.tar',
#                  'b7ff2716a6b0bd2caa3a4f4a84f8016913676782d5eb77526ad81be0a62b9619/layer.tar',
#                  'usr/lib/.wh.libformw.so.6'],
#     'extended-fullpath': [{
#         'type': 'tar',
#         'path': 'bash.tar'
#     }, {
#         'type': 'tar',
#         'path': 'b7ff2716a6b0bd2caa3a4f4a84f8016913676782d5eb77526ad81be0a62b9619/layer.tar'
#     }, {
#         'type': 'docker-whiteout',
#         'path': 'usr/lib/.wh.libformw.so.6'
#     }],
#     'timestamp': 1556193489,
#     'size': 0
# }

# TODO: add type hint for distro package match object

ExtendedObject = JsonDict
# ExtendedObject example:
# {
#     'name': 'mkmntdirs',
#     'fullpath': ['bash.tar',
#                  '0d2eaf4aa1a6112f04f5377ab5faee43703e2ded380b6109478f2db1fe0666bf/layer.tar', 'sbin/mkmntdirs'],
#     'extended-fullpath': [{
#                               'type': 'tar',
#                               'path': 'bash.tar'
#                           }, {
#                               'type': 'docker-layer',
#                               'path': '0d2eaf4aa1a6112f04f5377ab5faee43703e2ded380b6109478f2db1fe0666bf/layer.tar'
#                           }, {
#                               'type': 'elf',
#                               'path': 'sbin/mkmntdirs'
#                           }],
#     'timestamp': 1548276389,
#     'size': 13968,
#     'sha1': '2ad5d792e81a8feaf06a7ddc0dc8118e1e965250',
#     'confidence': 0.8,
#     'matching-method': 'distro-package-manager',
#     'binary-type': 'elf-executable-x86_64',
#     'package-name': 'alpine-baselayout',
#     'package-type': 'apk', <optional>
#     'package-version': '3.1.0-r3', <optional>
#     'distro': 'alpine', <optional>
#     'distro-version': '3.9.3', <optional>
#     'package-architecture': 'x86_64', <optional>
#     'type': 'distro-package',
#     'docker': {  <optional>
#         'image-id': '7f80652c1f4116a71fe90885c37c78feebd451fb4f50d7d323a0da209076c73a',
#         'layer-id': '0d2eaf4aa1a6112f04f5377ab5faee43703e2ded380b6109478f2db1fe0666bf/layer.tar'
#     }
# }

FindlibResult = JsonDict
# FindlibResult example:
# {
#     'lib': 'zsh',
#     'objects': ['zsh'],
#     'version': '5.6.2-r0',
#     'license': 'MIT',
#     'homepage': 'http://www.zsh.org',
#     'extended-objects':
#         [{
#              'name': 'zsh',
#              'fullpath': ['bash.tar', '3c3d21475/layer.tar',
#                           'bin/zsh'],
#              'extended-fullpath': [{
#                                        'type': 'tar',
#                                        'path': 'bash.tar'
#                                    }, {
#                                        'type': 'tar',
#                                        'path': '3c3d21475/layer.tar'
#                                    }, {
#                                        'type': 'elf',
#                                        'path': 'bin/zsh'
#                                    }],
#              'timestamp': 1545308087,
#              'size': 644536,
#              'exe-flags': ['no-fortify-source'],
#              'sha1': '8b7a1ecd3c27a05adad32366b382db64bc3a15ae',
#              'confidence': 0.9260504201680673,
#              'matching-method': 'signature',
#              'binary-type': 'elf-executable-x86_64',
#              'type': 'native'
#          }]
# }

FingerprintEntry = JsonDict
# FingerprintEntry example (not very comprehensive since there are PLENTY of optional fields):
# {
#     'added': 1384337904,
#     'aliases': ['http_server', 'apache_http_server', 'apache2'],
#     'homepage': 'https://httpd.apache.org/',
#     'lib': 'apache',
#     'license': 'Apache',
#     'proper-nvd': True,
#     'rodata': {
#         "string",
#         "another string",
#     },
#     'sources': ['/usr/sbin/apache2'],
#     'tags': ['protocol', 'server', 'http'],
#     'updated': 1384337904,
#     'vendor': 'apache',
#     'ver-regexp': 'Apache/(\\d+\\.\\d+\\.\\d+)'
# }

FingerprintDB = List[FingerprintEntry]
