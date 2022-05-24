# -*- coding: utf-8 -*-
"""Installer for the plone.autoinclude package."""

from setuptools import find_packages
from setuptools import setup


setup(
    name="plone.autoinclude",
    version="1.0.0a5",
    description="Auto include code and zcml",
    # long_description: see metadata in setup.cfg
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Framework :: Plone",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python",
    ],
    keywords="Python Plone CMS",
    author="Maurits van Rees",
    author_email="maurits@vanrees.org",
    url="https://github.com/collective/plone.autoinclude",
    project_urls={
        "PyPI": "https://pypi.org/project/plone.autoinclude/",
        "Source": "https://github.com/plone/plone.autoinclude",
        "Tracker": "https://github.com/plone/plone.autoinclude/issues",
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["plone"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.6",
    install_requires=[
        "setuptools",
        "zope.configuration",
    ],
)
