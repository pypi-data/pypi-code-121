# -*- coding: utf-8 -*-
###############################################################################
# PySword - A native Python reader of the SWORD Project Bible Modules         #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2019 Various PySword developers:                         #
# Kenneth Arnold, Joshua Gross, Tomas Groth, Ryan Hiebert, Philip Ridout,     #
# Matthew Wardrop                                                             #
# --------------------------------------------------------------------------- #
# Permission is hereby granted, free of charge, to any person obtaining a     #
# copy of this software and associated documentation files (the "Software"),  #
# to deal in the Software without restriction, including without limitation   #
# the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
# and/or sell copies of the Software, and to permit persons to whom the       #
# Software is furnished to do so, subject to the following conditions:        #
#                                                                             #
# The above copyright notice and this permission notice shall be included     #
# in all copies or substantial portions of the Software.                      #
#                                                                             #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER      #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
# DEALINGS IN THE SOFTWARE.                                                   #
###############################################################################

from pysword import __version__ as pysword_version
from setuptools import setup, find_packages


def read(filename):
    f = open(filename)
    text = f.read()
    f.close()
    return text

setup(
    name=u'pysword',
    version=pysword_version,
    packages=find_packages(exclude=[u'*.tests', u'*.tests.*', u'tests.*', u'tests']),
    url=u'https://gitlab.com/tgc-dk/pysword',
    license=u'MIT',
    author=u'Tomas Groth',
    author_email=u'second@tgc.dk',
    description=u'A native Python2/3 reader module for the SWORD Project Bible Modules',
    long_description=read(u'README.rst'),
    platforms=[u'any'],
    classifiers=[
        u'Development Status :: 4 - Beta',
        u'Intended Audience :: Religion',
        u'Intended Audience :: Developers',
        u'Operating System :: OS Independent',
        u'Programming Language :: Python :: 2',
        u'Programming Language :: Python :: 3',
        u'Topic :: Religion',
        u'Topic :: Software Development',
        u'License :: OSI Approved :: MIT License',
    ],
)
