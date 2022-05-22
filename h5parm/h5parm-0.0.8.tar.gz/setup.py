#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages

__maximum_numpy_version__ = '1.19.0'
__minimum_tables_version__ = '3.6.1'
__minimum_astropy_version__ = '4.0.0'

setup_requires = ['numpy<' + __maximum_numpy_version__,
                  'tables>=' + __minimum_tables_version__,
                  'astropy>=' + __minimum_astropy_version__]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='h5parm',
      version='0.0.8',
      description='H5Parm data pack interface',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/joshuaalbert/h5parm",
      author='Joshua G. Albert',
      author_email='albert@strw.leidenuniv.nl',
      setup_requires=setup_requires,
      tests_require=[
          'pytest>=2.8',
      ],
      package_data={'h5parm': ['arrays/*']},
      package_dir={'': './'},
      packages=find_packages('./'),
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: Apache Software License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.6',
      )
