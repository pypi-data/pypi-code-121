from ast import operator
import numpy
import pandas
from setuptools import setup, find_packages
import setuptools

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name= "match_recognize",
    version= '0.0.4',
    description= "match_recognize pattern detection",
    long_description= "match recognize support for python users with a built in automata",
    url= '',
    author='Mohga Emam',
    author_email='mohgasolimane@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords= ['match_recognize', 'pattern recognition', 'automata'],
    install_requires = ['numpy', 'pandas', 'operator', 'automata-lib']
)