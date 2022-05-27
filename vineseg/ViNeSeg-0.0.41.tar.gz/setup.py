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
    filename = "vineseg/__init__.py"
    with open(filename) as f:
        match = re.search(
            r"""^__version__ = ['"]([^'"]*)['"]""", f.read(), re.M
        )
    if not match:
        raise RuntimeError("{} doesn't contain __version__".format(filename))
    version = match.groups()[0]
    return version


def get_install_requires():
    PY3 = sys.version_info[0] == 3
    PY2 = sys.version_info[0] == 2
    assert PY3 or PY2

    install_requires = [
        "imgviz>=0.11",
        "matplotlib!=3.3",  # for PyInstaller
        "numpy",
        "Pillow>=2.8",
        "PyYAML",
        "qtpy!=1.11.2",
        "termcolor",
        "monai>=0.8.1",
        "torchmetrics>=0.8.2",
        "pandas",
        "scikit-image==0.18.1",
        "torchcontrib>=0.0.2",
        "shapely",
        "pyqt5",
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
        try:
            import PyQt4  # NOQA

            QT_BINDING = "pyqt4"
        except ImportError:
            if PY2:
                print(
                    "Please install PyQt5, PySide2 or PyQt4 for Python2.\n"
                    "Note that PyQt5 can be installed via pip for Python3.",
                    file=sys.stderr,
                )
                sys.exit(1)
            assert PY3
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
    


def main():
    version = get_version()

    if sys.argv[1] == "release":
        if not distutils.spawn.find_executable("twine"):
            print(
                "Please install twine:\n\n\tpip install twine\n",
                file=sys.stderr,
            )
            sys.exit(1)

        commands = [
            "python setup.py sdist",
            "twine upload dist/vineseg-{:s}.tar.gz".format(version),
        ]
        for cmd in commands:
            print("+ {:s}".format(cmd))
            subprocess.check_call(shlex.split(cmd))
        sys.exit(0)

    setup(
        name="ViNeSeg",
        version=version,
        packages=find_packages(exclude=["github2pypi"]),
        description="Image Polygonal Annotation with Python",
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        author="Nicolas Ruffini",
        author_email="nicolas.ruffini@lir-mainz.de",
        install_requires=get_install_requires(),
        license="GPLv3",
        keywords="Image Annotation, Machine Learning",
        classifiers=[
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: Implementation :: CPython",
            "Programming Language :: Python :: Implementation :: PyPy",
        ],
        package_data={"vineseg": ["icons/*", "config/*.yaml", "ai_pipeline/*", "visualization/*", "cascade2p/*", "widgets/*", "utils/*", "traces/*" ]},
        entry_points={
            "console_scripts": [
                "vineseg=vineseg.__main__:main",
            ],
        },
    )


if __name__ == "__main__":
    main()
