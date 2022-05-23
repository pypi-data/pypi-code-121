"""
To install KaniAttrDict:

    python setup.py install
"""
from setuptools import setup


DESCRIPTION = "A dict with attribute-style access"

try:
    LONG_DESCRIPTION = open('README.rst').read()
except:
    LONG_DESCRIPTION = DESCRIPTION


setup(
    name="kaniattrdict",
    version="3.0.1",
    author="Fx Kirin",
    author_email="fx.kirin@gmail.com",
    packages=("kaniattrdict",),
    url="",
    license="MIT License",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=(
        "Development Status :: 7 - Inactive",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ),
    install_requires=(
        'six',
    ),
    tests_require=(
        'nose>=1.0',
        'coverage',
    ),
    zip_safe=True,
)
