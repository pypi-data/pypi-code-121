#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='crimpl',
      version='0.1.0',
      description='Compute Resources Made Simple',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Kyle Conroy',
      author_email='kyleconroy@gmail.com',
      url='https://www.github.com/kecnry/crimpl',
      download_url = 'https://github.com/kecnry/crimpl/tarball/0.1.0',
      packages=['crimpl'],
      install_requires=['boto3'],
      classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
       ],
     )
