#!/usr/bin/env python
# coding: utf-8

# Define __version__ without importing msgpackrpc.
# This allows building sdist without installing any 3rd party packages.
exec(open("msgpackrpc/_version.py").read())

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="rpc-msgpack",
    version=__version__,
    author="Eatron Technologies",
    author_email="enes.toptas@eatron.com",
    description="RPC with MessagePack",
    long_description="""\
Updated version for MessagePack RPC for Python.

This implementation uses Tornado framework as a backend.

Original implementation:
https://github.com/msgpack-rpc/msgpack-rpc-python/
""",
    packages=["msgpackrpc", "msgpackrpc/transport"],
    install_requires=["msgpack >= 1.0.0", "tornado >= 6.1"],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
