#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['numpy', 'pandas', 'pingouin', 'graphviz', 'numba']

test_requirements = [ ]

setup(
    author="Yang Liu",
    author_email='yangliu@qmul.ac.uk',
    python_requires='>=3.6, <3.10',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A collection of Bayesian Network structure learning algorithms",
    entry_points={
        'console_scripts': [
            'bnsl=bnsl.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords='bnsl',
    name='bnsl',
    packages=find_packages(include=['bnsl', 'bnsl.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/Enderlogic/bnsl',
    version='0.1.14',
    zip_safe=False,
)
