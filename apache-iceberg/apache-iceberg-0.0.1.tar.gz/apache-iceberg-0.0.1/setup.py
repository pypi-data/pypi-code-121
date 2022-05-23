from setuptools import setup, find_packages

import os

setup(
    name='apache-iceberg',
    version='0.0.1',
    url='https://github.com/apache/iceberg',
    author='Apache Software Foundation',
    author_email='dev@iceberg.apache.org',
    description='Apache Iceberg is a new table format for storing large, slow-moving tabular data.',
    packages=find_packages(),    
    install_requires=[],
)

if not os.getenv("OVERRIDE"):
    raise RuntimeError('This is a placeholder for the Apache Iceberg Python library')

