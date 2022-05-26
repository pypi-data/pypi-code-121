# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 22:42:52 2022

@author: Asus
"""

from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='Algoritmosnumericos',
    version='0.2.5',
    description='maths algorithms and util funtion for plot numerical methods',
    long_description=open('README.txt').read()+'\n\n' +
    open('CHANGELOG.txt').read(),
    url='https://github.com/Ratabart666',
    author='Thomas Gomez',
    author_email='t.gomezs2@uniandes.edu.co',
    license='MIT',
    classifiers=classifiers,
    keywords='numerical methods',
    packages=find_packages(),
    install_requires=['numpy', 'scipy', 'statistic']
)
