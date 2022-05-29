#!/usr/bin/env python
# coding: utf-8

import setuptools

setuptools.setup(
    name='licsber',
    version=open('licsber/__init__.py').read()
        .split('\n')[0].lstrip('__version__ = ').strip("'"),
    author='Licsber',
    author_email='licsber@gmail.com',
    url='https://www.cnblogs.com/licsber/',
    description=u'个人娱乐工具箱.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'pymongo>=4.0',
        'requests',
        'tqdm',
    ],
    extras_require={
        'all': [
            'opencv-python',
            'paddlepaddle~=2.0',
            'beautifulsoup4',
            'pycryptodome',
            'minio',
            'h5py',
            'matplotlib',
            'torch',
            'torchvision',
            'ipywidgets',
        ],
        'dl': [
            'torch',
            'torchvision',
            'ipywidgets',
        ],
        'cv': [
            'opencv-python',
            'matplotlib',
        ],
        'wisedu': [
            'matplotlib',
            'opencv-python',
            'pycryptodome',
            'beautifulsoup4',
            'paddlepaddle~=2.0',
        ],
        'datasets': [
            'h5py',
        ],
        's3': [
            'minio',
        ],
    },
    entry_points={
        'console_scripts': [
            'licsber=licsber.shell.hello:licsber',
            'count-dir=licsber.shell.dir_ops:count_dir',
            'flatten-dir=licsber.shell.dir_ops:flatten_dir',
            'empty-dir=licsber.shell.dir_ops:empty_dir',
            'rename=licsber.shell.dir_ops:rename',
            's=licsber.shell.cloud_drive:save_115_dir',
            'memobird=licsber.shell.memobird:memobird',
            'sct=licsber.shell.server_chan:sct',
            'thumb=licsber.shell.thumb_gen:thumb_from_dir',
            'mi-merge=licsber.shell.mi_camera_merge:merge_dirs',
            'quark=licsber.shell.quark:upload_by_licsber_json',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: OS Independent',
    ],
    license='GPLv3',
)
