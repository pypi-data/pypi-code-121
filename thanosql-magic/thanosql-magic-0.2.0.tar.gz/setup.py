from codecs import open
from os import path

from setuptools import find_packages, setup

pkg_name = "thanosql-magic"

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

pkg_vars = {}
with open("thanosql/version.py") as f:
    exec(f.read(), pkg_vars)

setup(
    name=pkg_name,
    version=pkg_vars["__version__"],
    description="ThanoSQL Magic",
    long_description=long_description,
    url="https://github.com/smartmind-team/thanosql-magic",
    author="Dada Ahn",
    author_email="dada.ahn@smartmind.team",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="smartmind thanosql ipython jupyter",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=[
        "ipython",
        "requests",
        "pandas",
        "matplotlib",
    ],
    include_package_data=True,
    zip_safe=False,
)
