import os
from setuptools import setup

required = ['httplib2']

def get_version():
    with open(os.path.join('embedly', '__init__.py'), encoding="utf-8") as f:
        for line in f:
            if line.startswith('__version__ ='):
                return line.split('=')[1].strip().strip('"\'')

if os.path.exists("README.rst"):
    with open("README.rst", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "See https://github.com/embedly/embedly-python"


setup(
    name='embedly2',
    version=get_version(),
    author='Jelle Zijlstra',
    author_email='jelle.zijlstra@gmail.com',
    description='Python Library for Embedly',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="""
    Copyright (c) 2011, Embed.ly, Inc.
    All rights reserved.  Released under the 3-clause BSD license.
    """,
    url="https://github.com/JelleZijlstra/embedly2",
    packages=['embedly'],
    install_requires=required,
    test_suite="embedly.tests",
    zip_safe=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ]
)
