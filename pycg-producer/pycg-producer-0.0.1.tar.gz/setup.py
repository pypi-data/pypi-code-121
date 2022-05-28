#!/usr/bin/env python

from distutils.core import setup

setup(name='pycg-producer',
      version='0.0.1',
      license_files = ('LICENCE.txt',),
      description='Call Graph Producer for PyPI Packages with the use of PyCG ',
      author='Georgios-Petros Drosos',
      author_email='drosos007@gmail.com',
      url='https://github.com/fasten-project/pypi-tools/tree/main/cg-producer',
      packages=['pycg_producer'],
      install_requires=['pycg==0.0.5'],
     )