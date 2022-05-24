#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import os, sys

github_url = "https://github.com/luciano-im"
twitter_url = "https://twitter.com/luciano_dev"
package_name = "django-custom-url"
package_url = "{}/{}".format(github_url, package_name)
package_path = os.path.abspath(os.path.dirname(__file__))
long_description_file_path = os.path.join(package_path, "README.md")
long_description_content_type = "text/markdown"
long_description = ""
try:
    long_description_file_options = (
        {} if sys.version_info[0] < 3 else {"encoding": "utf-8"}
    )
    with open(long_description_file_path, "r", **long_description_file_options) as f:
        long_description = f.read()
except IOError:
    pass

setup(
    name=package_name,
    packages=find_packages(),
    version=0.2,
    description="A Django app to easily manage custom url linked to static files.",
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    author="Luciano Muñoz",
    author_email="hola@luciano.im",
    url=package_url,
    # download_url="{}/archive/{}.tar.gz".format(package_url, 0.1),
    project_urls={
        "Documentation": "{}#readme".format(package_url),
        "Issues": "{}/issues".format(package_url),
        "Twitter": twitter_url,
    },
    keywords=[
        "django",
        "custom",
        "url",
        "path",
        "file url",
        "file path",
    ],
    install_requires=[
        "Django >= 3.0",
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Build Tools",
    ],
    license="MIT",
    include_package_data = True,
)