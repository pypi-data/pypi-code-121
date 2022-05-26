from setuptools import setup, find_packages

import rapyuta_io

with open("README.md", encoding="utf-8") as f:
    long_desc = f.read()


setup(
    name="rapyuta_io",
    version=rapyuta_io.__version__,
    description="Rapyuta.io Python SDK",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="Rapyuta Robotics",
    author_email="opensource@rapyuta-robotics.com",
    packages=find_packages(include=["rapyuta_io*"]),
    python_requires=">=3.6",
    license="Apache 2.0",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=[
        "requests>=2.20.0",
        "six>=1.13.0",
        "urllib3>=1.23",
        "python-dateutil>=2.8.2",
        "pytz",
        "setuptools",
    ],
    extras_require={
        "dev": ["sphinx", "furo"],
        "test": [
            "testtools",
            "pyfakefs",
            "mock",
        ],
    },
)
