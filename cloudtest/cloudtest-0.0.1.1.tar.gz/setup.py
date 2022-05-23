#!/usr/bin/env python
# # coding: utf-8

from setuptools import setup
__version__ = "0.0.1.1"

setup(
    name='cloudtest',
    description='cloudtest',
    long_description='used for test openstack projects',
    version=__version__,
    author='Juewuer',
    author_email='lihechao@gmail.com',
    license="MIT",
    url='https://github.com/juewuer/cloudtest',
    py_modules=['cloudtest'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Testing',
    ],
)
