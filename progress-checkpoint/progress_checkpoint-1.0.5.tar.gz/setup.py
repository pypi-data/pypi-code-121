#!/usr/bin/env python

from setuptools import setup


with open("README.md") as fh:
    long_description = fh.read()

setup(
    name='progress_checkpoint',
    version='1.0.5',
    description='Helpers for reporting a progress from functions by the means of callbacks.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url='https://github.com/peper0/progress-checkpoint',
    author='Tomasz Lakota',
    author_email='tomasz.lakota@gmail.com',
    install_requires=[
        'deprecation',
    ],
    tests_require=[
    ],
    extras_require={
        'progressbar': ['progressbar'],
    },
    package_data={
        'progress_checkpoint': ['py.typed'],
    },
    packages=('progress_checkpoint',),
    keywords=[
        'progress', 'progressbar', 'callback', 'reporting'
        ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    python_requires='>=3.6'
)
