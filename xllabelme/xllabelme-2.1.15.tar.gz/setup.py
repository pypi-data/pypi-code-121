#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import distutils.spawn
import os
import re
import shlex
import subprocess
import sys

from setuptools import find_packages
from setuptools import setup


def get_version():
    filename = "xllabelme/__init__.py"
    with open(filename, encoding='utf8') as f:
        match = re.search(
            r"""^version\s*=\s*['"]([^'"]*)['"]""", f.read(), re.M
        )
    if not match:
        raise RuntimeError("{} doesn't contain __version__".format(filename))
    version = match.group(1)
    return version


def get_install_requires():
    PY3 = sys.version_info[0] == 3
    PY2 = sys.version_info[0] == 2
    assert PY3 or PY2

    # 试了py3.6、py3.8，都是能编译exe成功的
    install_requires = [
        "pyxllib>=0.2.14.1",
        # "imgviz==1.2.1",  # 这个限定不用，新版imgviz又兼容了
        "imgviz>=0.11",
        "matplotlib<3.3",  # for PyInstaller
        # "matplotlib",  # 这个版本确实不能升，会有问题，先不要改
		"natsort>=7.1.0",
        "numpy",
        "Pillow>=2.8",
        "PyYAML",
        "qtpy!=1.11.2",
        "termcolor",
    ]

    # Find python binding for qt with priority:
    # PyQt5 -> PySide2 -> PyQt4,
    # and PyQt5 is automatically installed on Python3.
    QT_BINDING = None

    try:
        import PyQt5  # NOQA

        QT_BINDING = "pyqt5"
    except ImportError:
        pass

    if QT_BINDING is None:
        try:
            import PySide2  # NOQA

            QT_BINDING = "pyside2"
        except ImportError:
            pass

    if QT_BINDING is None:
        # PyQt5 can be installed via pip for Python3
        # 5.15.3, 5.15.4 won't work with PyInstaller
        install_requires.append("PyQt5!=5.15.3,!=5.15.4")
        QT_BINDING = "pyqt5"

    del QT_BINDING

    if os.name == "nt":  # Windows
        install_requires.append("colorama")

    return install_requires


def get_long_description():
    with open("README.md") as f:
        long_description = f.read()
    try:
        # when this package is being released
        import github2pypi

        return github2pypi.replace_url(
            slug="wkentaro/labelme", content=long_description, branch="main"
        )
    except ImportError:
        # when this package is being installed
        return long_description


def main():
    version = get_version()

    if sys.argv[1] == "release":
        try:
            import github2pypi  # NOQA
        except ImportError:
            print(
                "Please install github2pypi\n\n\tpip install github2pypi\n",
                file=sys.stderr,
            )
            sys.exit(1)

        if not distutils.spawn.find_executable("twine"):
            print(
                "Please install twine:\n\n\tpip install twine\n",
                file=sys.stderr,
            )
            sys.exit(1)

        commands = [
            "git push origin main",
            "git tag v{:s}".format(version),
            "git push origin --tags",
            "python setup.py sdist",
            "twine upload dist/labelme-{:s}.tar.gz".format(version),
        ]
        for cmd in commands:
            print("+ {:s}".format(cmd))
            subprocess.check_call(shlex.split(cmd))
        sys.exit(0)

    setup(
        name="xllabelme",
        version=version,
        packages=find_packages(exclude=["github2pypi"]),
        description="Image Polygonal Annotation with Python",
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        author="code4101,Kentaro Wada",
        author_email="877362867@qq.com",
        url="https://github.com/XLPRUtils/xllabelme",
        install_requires=get_install_requires(),
        license="GPLv3",
        keywords="Image Annotation, Machine Learning",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3 :: Only",
        ],
        package_data={"xllabelme": ["icons/*", "config/*.yaml"]},
        entry_points={
            "console_scripts": [
                "xllabelme=xllabelme.__main__:main",
                "xllabelme_draw_json=xllabelme.cli.draw_json:main",
                "xllabelme_draw_label_png=xllabelme.cli.draw_label_png:main",
                "xllabelme_json_to_dataset=xllabelme.cli.json_to_dataset:main",
                "xllabelme_on_docker=xllabelme.cli.on_docker:main",
            ],
        },
        data_files=[("share/man/man1", ["docs/man/labelme.1"])],
    )


if __name__ == "__main__":
    main()
