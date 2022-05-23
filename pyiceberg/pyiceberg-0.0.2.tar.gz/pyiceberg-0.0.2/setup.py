from setuptools import setup, find_packages
from setuptools.command.install import install

import os

class post_install(install):
    def run(self):
        raise RuntimeError('This is a placeholder for the Apache Iceberg Python library')

setup(
    name='pyiceberg',
    version='0.0.2',
    url='https://github.com/apache/iceberg',
    author='Apache Software Foundation',
    author_email='dev@iceberg.apache.org',
    description='Apache Iceberg is a new table format for storing large, slow-moving tabular data.',
    packages=find_packages(),
    install_requires=[],
    cmdclass={'install': post_install},
)
