# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

INSTALL_REQUIRE = [
    "feast==0.19.*",
    "mysql-connector-python==8.0.28",
    "pyarrow>=2.0.0",
]

DEV_REQUIRE = [
    "flake8",
    "black==21.10b0",
    "isort>=5",
    "mypy==0.790",
    "build==0.7.0",
    "twine==3.4.2",
    "pytest>=6.0.0",
]

setup(
    name="feast-mysql",
    version="0.3.2",
    author="Shaped",
    author_email="shai@shaped.ai",
    description="MySQL registry and offline store for Feast",
    long_description=readme,
    long_description_content_type="text/markdown",
    python_requires=">=3.7.0",
    url="https://github.com/shaped-ai/feast-mysql",
    project_urls={
        "Bug Tracker": "https://github.com/shaped-ai/feast-mysql/issues",
    },
    license="Apache License, Version 2.0",
    packages=["feast_mysql", "feast_mysql.offline_store"],
    install_requires=INSTALL_REQUIRE,
    extras_require={
        "dev": DEV_REQUIRE,
    },
    keywords=("feast featurestore mysql offlinestore"),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
