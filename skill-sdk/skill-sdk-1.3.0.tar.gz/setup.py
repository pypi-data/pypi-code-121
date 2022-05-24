#!/usr/bin/env python

import os
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(HERE, "skill_sdk", "__version__.py")) as f:
    exec(f.read(), about)


setup(
    name=about["__name__"],
    version=about["__version__"],
    description=about["__description__"],
    url=about["__url__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    license=about["__license__"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    packages=find_packages(),
    package_data={
        "": ["*"],
        "skill_sdk.cli": [
            "scaffold/*",
            "scaffold/impl/*",
            "scaffold/locale/*",
            "scaffold/scripts/*",
            "scaffold/tests/*",
        ],
        "skill_sdk.ui": ["css/*", "js/*", "templates/*"],
    },
    install_requires=[
        "fastapi>=0.70.0,<1",
        "pydantic>=1.8,<2.0.0",
        "starlette_context",
        "python-dateutil",
        "babel",
        "uvicorn[standard]",
        "isodate",
        "orjson",
        "aiobreaker",
        "httpx>=0.16, <1",
        "pyyaml",
        "nest-asyncio",
        "pycryptodome",
        "Crypto~=1.4.1"
    ],
    extras_require={
        "dev": [
            "gunicorn",
            "starlette[full]",
            "mypy>=0.9",
            "respx",
            "black",
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "pytest-asyncio",
            "questionary",
            "starlette-opentracing",
            "jaeger-client",
            "starlette-exporter",
            "types-orjson",
            "types-python-dateutil",
            "types-pkg_resources",
            "types-PyYAML",
        ],
        "all": [
            "starlette-opentracing",
            "starlette-exporter",
        ],
    },
    entry_points={"console_scripts": ["vs = skill_sdk.__main__:main"]},
    setup_requires=["wheel"],
    python_requires=">=3.7",
)
