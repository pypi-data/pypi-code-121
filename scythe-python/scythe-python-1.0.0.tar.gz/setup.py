# -*- coding: utf-8 -*-
from setuptools import setup


install_requires = ['requests']

setup(
    name='scythe-python',
    version='1.0.0',
    author='YAT, LLC',
    author_email='robertgoss07@gmail.com',
    packages=['scythe'],
    license="MIT",
    install_requires=install_requires,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description='Python SDK for Scythe',
    long_description=open('README.md').read(),
    zip_safe=True,
)