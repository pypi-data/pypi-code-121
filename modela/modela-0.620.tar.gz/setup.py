#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'modelaapi', 'tabulate', 'tqdm', 'protobuf', 'grpcio', 'jwt', 'typing_utils', 'pandas',
                'protoc-gen-swagger', 'grpc-interceptor']

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Metaprov",
    author_email='support@metaprov.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Modela Automatic Machine Learning SDK",
    entry_points={
        'console_scripts': [
            'modela=modela.cli:main',
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n',
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='modela',
    name='modela',
    packages=find_packages(include=['modela', 'modela.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/metaprov/modela-python-sdk',
    version='0.620',
    zip_safe=False,
)
