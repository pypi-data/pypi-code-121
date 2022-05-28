#!/usr/bin/python3
# -*- coding: utf-8 -*-


from setuptools import setup
from subtrs.__metadata__ import __version__


INSTALLATION_REQUIREMENTS = ['googletrans==3.1.0a0',
                             'colored>=1.4.3',
                             'progress>=1.6'
                             ]
DOCS_REQUIREMENTS = []
OPTIONAL_REQUIREMENTS = []


setup(
    name='subtrs',
    packages=['subtrs'],
    scripts=['bin/subtrs'],
    version=__version__,
    description='A simple tool that translates video subtitles',
    long_description=open('README.rst').read(),
    keywords=['video', 'translate', 'subtitles', 'google', 'youtube'],
    author='Dimitris Zlatanidis',
    author_email='d.zlatanidis@gmail.com',
    package_data={'': ['README.rst', 'CHANGES.md']},
    data_files=[],
    url='https://gitlab.com/dslackw/subtrs',
    install_requires=INSTALLATION_REQUIREMENTS,
    extras_require={
        'optional': OPTIONAL_REQUIREMENTS,
        'docs': DOCS_REQUIREMENTS,
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.9',
        'Topic :: Text Processing',
        'Topic :: Terminals',
        ],
    python_requires='>=3.9'
)
