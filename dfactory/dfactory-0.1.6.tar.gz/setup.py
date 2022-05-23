"""
setup.py
"""

# !/usr/bin/env python
# coding=utf-8
import platform
from os.path import join, dirname

from setuptools import setup, find_packages

NAME = 'dfactory'
DESCRIPTION = 'a data pipeline framework'
URL = 'https://github.com/skiloop/dfactory'
EMAIL = 'skiloop@gmail.com'
AUTHOR = 'skiloop'
SYSTEM = platform.system()

with open(join(dirname(__file__), 'dfactory/VERSION'), 'rb') as fversion:
    VERSION = fversion.read().decode('ascii').strip()
with open('README.md', encoding="utf-8") as frm:
    long_desc = frm.read()
setup(
    name=NAME,
    version=VERSION,
    url=URL,
    project_urls={
        'Source': URL,
        'Tracker': 'https://github.com/skiloop/dfactory/issues',
    },
    description=DESCRIPTION,
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    maintainer=AUTHOR,
    maintainer_email=EMAIL,
    license='MIT',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['scrapy = scrapy.cmdline:execute']
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    install_requires=[],
    extras_require={},
)
