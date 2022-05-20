#!/usr/bin/env python

# Copyright (c) 2016-2022 Knuth Project developers.
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import glob
import os
import platform
import shutil
import stat
import sys

from setuptools import setup, find_packages
from setuptools.extension import Extension
from distutils import dir_util, file_util
from distutils import log
from setuptools.command.install_lib import install_lib
from setuptools.command.install import install
from setuptools.command.develop import develop
# from setuptools.command.egg_info import egg_info
from setuptools.command.build_ext import build_ext

from distutils.command.build import build
from setuptools.command.install import install

from setuptools.dist import Distribution
from conans.client.conan_api import (Conan, default_manifest_folder)
import fnmatch

from sys import platform

PKG_NAME = 'kth-py-native'
# VERSION = '1.1.9'
SYSTEM = sys.platform


def get_similar_lib(path, pattern):
    # for file in os.listdir('.'):
    #     if fnmatch.fnmatch(file, '*.txt'):
    #         print file
    for file in os.listdir(path):
        if fnmatch.fnmatch(file, pattern):
            return file
    return ""


# if platform == "linux" or platform == "linux2":
#     # linux
# elif platform == "darwin":
#     # OS X
# elif platform == "win32":
#     # Windows...

def get_libraries():
    # libraries = ['kth-c-api', 'kth-node', 'kth-blockchain', 'kth-network', 'kth-consensus', 'kth-database', 'kth-core', 'boost_atomic', 'boost_chrono', 'boost_date_time', 'boost_filesystem', 'boost_iostreams', 'boost_locale', 'boost_log', 'boost_log_setup', 'boost_program_options', 'boost_random', 'boost_regex', 'boost_system', 'boost_unit_test_framework', 'boost_prg_exec_monitor', 'boost_test_exec_monitor', 'boost_thread', 'boost_timer', 'secp256k1', 'bz2', 'gmp', 'z',]
    fixed = ['kth/lib/kth-c-api', 'kth/lib/kth-node', 'kth/lib/kth-blockchain', 'kth/lib/kth-network', 'kth/lib/kth-consensus', 'kth/lib/kth-database', 'kth/lib/kth-domain', 'kth/lib/kth-infrastructure']


    if platform == "win32":
        # libraries = ['boost_atomic', 'boost_chrono', 'boost_date_time', 'boost_filesystem', 'boost_iostreams', 'boost_locale', 'boost_log', 'boost_log_setup', 'boost_program_options', 'boost_random', 'boost_regex', 'boost_system', 'boost_unit_test_framework', 'boost_prg_exec_monitor', 'boost_test_exec_monitor', 'boost_thread', 'boost_timer', 'secp256k1', 'bz2', 'mpir', 'z',]
        # libraries = ['boost_atomic', 'boost_chrono', 'boost_date_time', 'boost_filesystem', 'boost_iostreams', 'boost_locale', 'boost_log', 'boost_log_setup', 'boost_program_options', 'boost_random', 'boost_regex', 'boost_system', 'boost_unit_test_framework', 'boost_prg_exec_monitor', 'boost_test_exec_monitor', 'boost_thread', 'boost_timer', 'secp256k1', 'mpir', 'z',]
        libraries = ['boost_atomic', 'boost_chrono', 'boost_date_time', 'boost_filesystem', 'boost_iostreams', 'boost_locale', 'boost_log', 'boost_log_setup', 'boost_program_options', 'boost_random', 'boost_regex', 'boost_system', 'boost_unit_test_framework', 'boost_prg_exec_monitor', 'boost_test_exec_monitor', 'boost_thread', 'boost_timer', 'secp256k1', 'mpir', 'lmdb']
        winlibs = fixed
        for lib in libraries:
            # print(lib)
            xxx = get_similar_lib('kth/lib', "*" + lib + "*")
            if xxx != '':
                xxx = xxx.replace('.lib', '')
                # print(xxx)
                winlibs.append(xxx)

        # print(winlibs)
        return winlibs
    else:
        # libraries = ['boost_atomic', 'boost_chrono', 'boost_date_time', 'boost_filesystem', 'boost_iostreams', 'boost_locale', 'boost_log', 'boost_log_setup', 'boost_program_options', 'boost_random', 'boost_regex', 'boost_system', 'boost_unit_test_framework', 'boost_prg_exec_monitor', 'boost_test_exec_monitor', 'boost_thread', 'boost_timer', 'secp256k1', 'bz2', 'gmp', 'z',]
        # libraries = ['boost_atomic', 'boost_chrono', 'boost_date_time', 'boost_filesystem', 'boost_iostreams', 'boost_locale', 'boost_log', 'boost_log_setup', 'boost_program_options', 'boost_random', 'boost_regex', 'boost_system', 'boost_unit_test_framework', 'boost_prg_exec_monitor', 'boost_test_exec_monitor', 'boost_thread', 'boost_timer', 'secp256k1', 'gmp', 'z',]
        libraries = ['kth/lib/boost_atomic', 'kth/lib/boost_chrono', 'kth/lib/boost_date_time', 'kth/lib/boost_filesystem', 'kth/lib/boost_iostreams', 'kth/lib/boost_locale', 'kth/lib/boost_log', 'kth/lib/boost_log_setup', 'kth/lib/boost_program_options', 'kth/lib/boost_random', 'kth/lib/boost_regex', 'kth/lib/boost_system', 'kth/lib/boost_unit_test_framework', 'kth/lib/boost_prg_exec_monitor', 'kth/lib/boost_test_exec_monitor', 'kth/lib/boost_thread', 'kth/lib/boost_timer', 'kth/lib/secp256k1', 'kth/lib/gmp', 'kth/lib/lmdb']
        # libraries = []
        return fixed + libraries

def do_conan_stuff(microarch=None, currency=None):

    # if not microarch:
    #     microarch = 'x86_64'

    print('do_conan_stuff microarch currency')
    print(microarch)

    # New API in Conan 0.28
    c, _, _ = Conan.factory()

    try:
        # c.remote_add(remote, url, verify_ssl, args.insert)
        c.remote_add('kth', 'https://knuth.jfrog.io/artifactory/api/conan/knuth')
    except:
        print ("Conan Remote exists, ignoring exception")

    refe = "."

    opts = None

    # if microarch:
    #     # c.install(refe, verify=None, manifests=None)
    #     opts = ['*:microarchitecture=%s' % (microarch,)]
    #     c.install(refe, verify=None, manifests_interactive=None, manifests=None, options=opts)
    # else:
    #     c.install(refe, verify=None, manifests_interactive=None, manifests=None)

    if microarch:
        opts = ['*:microarchitecture=%s' % (microarch,)]

    if currency:
        if opts:
            opts.append('*:currency=%s' % (currency,))
        else:
            opts = ['*:currency=%s' % (currency,)]

    c.install(refe, verify=None, manifests_interactive=None, manifests=None, options=opts)



def do_build_stuff(microarch=None, currency=None):

    print('*********************************************************************************************************')
    print(os.path.dirname(os.path.abspath(__file__)))
    print(os.getcwd())
    print('*********************************************************************************************************')

    prev_dir = os.getcwd()

    do_conan_stuff(microarch, currency)

    print('*********************************************************************************************************')
    print(os.path.dirname(os.path.abspath(__file__)))
    print(os.getcwd())
    print('*********************************************************************************************************')

    os.chdir(prev_dir)

    print('*********************************************************************************************************')
    print(os.path.dirname(os.path.abspath(__file__)))
    print(os.getcwd())
    print('*********************************************************************************************************')

    # extensions[0].libraries = get_libraries()
    # extensions[0].extra_objects = get_libraries()


class DevelopCommand(develop):
    user_options = develop.user_options + [
        ('microarch=', None, 'CPU microarchitecture'),
        ('currency=', None, 'Cryptocurrency')
    ]

    def initialize_options(self):
        develop.initialize_options(self)
        self.microarch = None
        self.currency = None

    def finalize_options(self):
        develop.finalize_options(self)

    def run(self):
        global microarch
        microarch = self.microarch

        global currency
        currency = self.currency

        print('*********************************** DevelopCommand run microarch currency')
        print(microarch)
        print(currency)

        do_build_stuff(microarch, currency)

        develop.run(self)



class InstallCommand(install):
    user_options = install.user_options + [
        ('microarch=', None, 'CPU microarchitecture'),
        ('currency=', None, 'Cryptocurrency')
    ]

    def initialize_options(self):
        install.initialize_options(self)
        self.microarch = None
        self.currency = None

    def finalize_options(self):
        install.finalize_options(self)

    def run(self):
        global microarch
        microarch = self.microarch

        global currency
        currency = self.currency

        print('*********************************** InstallCommand run microarch currency')
        print(microarch)
        print(currency)

        do_build_stuff(microarch, currency)

        install.run(self)


class BuildCommand(build):
    user_options = build.user_options + [
        ('microarch=', None, 'CPU microarchitecture'),
        ('currency=', None, 'Cryptocurrency')
    ]

    def initialize_options(self):
        build.initialize_options(self)
        self.microarch = None
        self.currency = None

    def finalize_options(self):
        build.finalize_options(self)

    def run(self):
        global microarch
        microarch = self.microarch

        global currency
        currency = self.currency

        print('--------------------------------------- BuildCommand run microarch currency')
        print(microarch)
        print(currency)

        do_build_stuff(microarch, currency)

        build.run(self)


# ------------------------------------------------

microarch = ''

extensions = [
	Extension('kth_native',
        define_macros = [
            ('KTH_LIB_STATIC', None),
            ('KTH_DB_NEW_FULL', None),
            ('KTH_LOG_LIBRARY_SPDLOG', None),
            ('KTH_CURRENCY_BCH', None),
        ],

        # 'binary.c'
        # 'chain/word_list.c',

    	sources = [
            'src/utils.c',
            'src/chain/header.c',
            'src/chain/block.c',
            'src/chain/merkle_block.c',
            'src/node.cpp',
            'src/chain/chain.c',
            'src/chain/point.c',
            'src/chain/history.c',
            'src/chain/transaction.c',
            'src/chain/output.c',
            'src/chain/output_list.c',
            'src/chain/input.c',
            'src/chain/input_list.c',
            'src/chain/script.c',
            'src/chain/payment_address.c',
            'src/chain/compact_block.c',
            'src/chain/output_point.c',
            'src/chain/block_list.c',
            'src/chain/transaction_list.c',
            'src/chain/stealth_compact.c',
            'src/chain/stealth_compact_list.c',
            'src/p2p/p2p.c',

            'src/config/database_settings.cpp',
            'src/config/node_settings.cpp',

            'src/module.c',

        ],

        include_dirs=['kth/include', 'include'],
        # library_dirs=['kth/lib'],


        extra_objects = [
            'kth/lib/libkth-c-api.a',
            'kth/lib/libkth-node.a',
            'kth/lib/libkth-blockchain.a',
            'kth/lib/libkth-network.a',
            'kth/lib/libkth-consensus.a',
            'kth/lib/libkth-database.a',
            'kth/lib/libkth-domain.a',
            'kth/lib/libkth-infrastructure.a',
            'kth/lib/libboost_atomic.a',
            'kth/lib/libboost_chrono.a',
            'kth/lib/libboost_date_time.a',
            'kth/lib/libboost_filesystem.a',
            'kth/lib/libboost_iostreams.a',
            'kth/lib/libboost_locale.a',
            'kth/lib/libboost_log.a',
            'kth/lib/libboost_log_setup.a',
            'kth/lib/libboost_program_options.a',
            'kth/lib/libboost_random.a',
            'kth/lib/libboost_regex.a',
            'kth/lib/libboost_system.a',
            'kth/lib/libboost_unit_test_framework.a',
            'kth/lib/libboost_prg_exec_monitor.a',
            'kth/lib/libboost_test_exec_monitor.a',
            'kth/lib/libboost_thread.a',
            'kth/lib/libboost_timer.a',
            'kth/lib/libsecp256k1.a',
            'kth/lib/libgmp.a',
            'kth/lib/liblmdb.a'
        ]
    ),
]

exec(open('./version.py').read())
setup(
    name=PKG_NAME,
    # version=VERSION,
    version=__version__,

    python_requires=">=3.4",

    description='Knuth Project',
    long_description='Knuth Project',
    url='https://github.com/k-nuth/py-native',

    # Author details
    author='Knuth Project',
    author_email='info@kth.cash',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Programming Language :: C++',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],

    # What does your project relate to?
    keywords='bitcoin cash bch money knuth kth',

    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    ext_modules = extensions,

    cmdclass={
        'build': BuildCommand,
        'install': InstallCommand,
        'develop': DevelopCommand,
        # 'egg_info': EggInfoCommand,

    },

)
