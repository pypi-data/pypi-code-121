'''
File: setup.py
Project: pyautd
Created Date: 10/09/2020
Author: Shun Suzuki
-----
Last Modified: 23/05/2022
Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
-----
Copyright (c) 2021 Hapis Lab. All rights reserved.
'''


import setuptools


def _get_version():
    with open('README.md', 'r') as f:
        for line in f.readlines():
            if line.startswith('version: '):
                return line.replace('version: ', '').strip()
    raise LookupError('version info is not found in README.md')


def _set_package_version(version):
    init_py = ''
    with open('pyautd3/__init__.py', 'r') as f:
        for line in f.readlines():
            if line.startswith('__version__'):
                line = '__version__ = \'' + version.strip() + '\'\n'
            init_py = init_py + line

    with open('pyautd3/__init__.py', 'w') as f:
        f.write(init_py)


with open('README.md', 'r') as fh:
    long_description = fh.read()

_set_package_version(_get_version())

setuptools.setup(
    name='pyautd3',
    version=_get_version(),
    author='Shun Suzuki',
    author_email='suzuki@hapis.k.u-tokyo.ac.jp',
    description='AUTD3 library wrapper for python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['requests'],
    url='https://github.com/shinolab/pyautd',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: MacOS'
    ],
    license='See https://github.com/shinolab/pyautd',
    platforms=["Windows", "Linux", "Mac OS-X"],
    include_package_data=True,
    package_dir={'pyautd3': 'pyautd3'},
    packages=['pyautd3'],
    python_requires='>=3.7',
)
