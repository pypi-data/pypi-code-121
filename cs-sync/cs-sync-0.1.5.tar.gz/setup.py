#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setuptools


with open('README.md', 'r') as fin:
    long_description = fin.read()
with open('LICENSE', 'r') as fin:
    license = fin.read()

setuptools.setup(
    name='cs-sync',
    version='0.1.5',
    license='MIT',
    author='Kyle L. Davis',
    author_email='AceofSpades5757.github@gmail.com',
    install_requires=[
        'typer',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AceofSpades5757/cs-sync',
    python_requires='>=3.6',
    packages=setuptools.find_packages('src'),
    package_dir={
        '': 'src',
        'cs_sync': 'src/cs_sync',
    },
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    entry_points={
        'console_scripts': [
            'cs-sync = cs_sync.main:cli',
        ],
    },
)
