# -*- coding: utf-8 -*-
"""
Created on Fri May 27 15:00:40 2022

@author: UCC
"""

from setuptools import setup, find_packages


setup(
    name='Topographic Calculation for Python Library',
    version='0.0.1.dev0',
    license='gpl-3.0',
    author="Utku Can CANATAN",
    author_email='utkucancanatan@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/utkucanc/Topographic-Calc',
    keywords='TCPL',
    install_requires=[
          'math',
      ],

)