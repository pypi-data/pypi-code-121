#!/usr/bin/env python
import platform
import sys
from glob import glob
from os.path import join, dirname
import imp

try:
    # Use setuptools if available, for install_requires (among other things).
    from setuptools import setup, find_packages, Extension  # lgtm[py/import-of-mutable-attribute]
    setuptools = True
except ImportError:
    from distutils.core import setup, find_packages, Extension  # lgtm[py/import-of-mutable-attribute]
    setuptools = False

# Classic setup.py

kwargs = {}

# Version configuration
version = imp.load_source('version', join(dirname(__file__), 'rook', 'version.py')).VERSION

# Readme
with open('README.rst') as f:
    kwargs['long_description'] = f.read()

if sys.platform in ('darwin', 'linux2', 'linux'):
    ext_modules = []
    extra_compile_args = [
        '-std=c++0x',
        '-g0',
        '-O3',
        '-Wno-deprecated-register']
    extra_link_args = []

    if sys.platform == 'darwin':
        mac_version = platform.mac_ver()[0]
        extra_compile_args.append("-mmacosx-version-min=" + mac_version)
        extra_link_args.append("-Xlinker -macosx_version_min " + mac_version)

    if ('CPython' == platform.python_implementation()) and \
            ((sys.version_info[0] == 2 and sys.version_info > (2, 7, 0)) or
             (sys.version_info[0] == 3 and sys.version_info >= (3, 5, 0))):
        ext_modules.append(Extension(
            'rook.services.cdbg_native',
            sources=glob('rook/services/exts/cloud_debug_python/*.cc'),
            extra_compile_args=extra_compile_args, extra_link_args=extra_link_args))

    ext_modules.append(Extension(
        'native_extensions',
        sources=glob('rook/native_extensions/*.cc'),
        extra_compile_args=extra_compile_args, extra_link_args=extra_link_args))

    kwargs['ext_modules'] = ext_modules


if setuptools:
    # If setuptools is not available, you're on your own for dependencies.
    install_requires = [
        "six >= 1.13",
        "protobuf >= 3.7.1, <= 4.0.0; python_version > '3.0'",
        "protobuf >= 3.7.1, < 3.18; python_version < '3.0'",
        "websocket-client >= 0.56, != 0.58, != 0.59, != 1.0, != 1.1",
        "psutil >= 5.8.0",
        "certifi",
        "funcsigs",
        "distro"
    ]

    kwargs['install_requires'] = install_requires

setup(
    name="rook",
    version=version,
    packages=find_packages(where='.', exclude=['contrib', 'docs', '*test*']),
    include_package_data=True,
    author="Rookout",
    author_email="liran@rookout.com",
    url="http://rookout.com/",
    description="Rook is a Python package for on the fly debugging and data extraction for application in production",
    license="https://get.rookout.com/SDK_LICENSE.pdf",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',

        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',

    ],
    zip_safe=False,
    extras_require={
        'ssl_backport': ['backports.ssl', 'backports.ssl_match_hostname', 'PyOpenSSL'],        
    },
    **kwargs
)
