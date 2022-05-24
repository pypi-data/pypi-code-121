#!/usr/bin/env python

from pathlib import Path

try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    raise ImportError(
        'Could not import "setuptools".' "Please install the setuptools package."
    )


README = Path("./README.md")
LICENSE = Path("./LICENSE").read_text()
version = "0.4"

NAME = "wechat_enterprise_sdk"
VERSION = version
DESCRIPTION = ""
KEYWORDS = "python wechat enterprise, wechat_enterprise,send message"
AUTHOR = "somenzz"
AUTHOR_EMAIL = "somenzz@163.com"
URL = "https://github.com/somenzz/wechat_enterprise"
PACKAGES = ["wechat_enterprise"]
INSTALL_REQUIRES = ["requests", "requests_toolbelt"]
TEST_SUITE = ""
TESTS_REQUIRE = []

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Topic :: Software Development",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities",
]


params = {
    "name": NAME,
    "version": VERSION,
    "description": DESCRIPTION,
    "keywords": KEYWORDS,
    "author": AUTHOR,
    "author_email": AUTHOR_EMAIL,
    "url": URL,
    "license": "MIT",
    "packages": PACKAGES,
    "install_requires": INSTALL_REQUIRES,
    "tests_require": TESTS_REQUIRE,
    "test_suite": TEST_SUITE,
    "classifiers": CLASSIFIERS,
    "zip_safe": False,
    "long_description": README.read_text(),
}

if __name__ == "__main__":
    setup(**params, long_description_content_type="text/markdown")
