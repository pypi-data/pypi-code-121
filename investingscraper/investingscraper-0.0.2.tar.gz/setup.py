from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 2 - Pre-Alpha",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Operating System :: Microsoft :: Windows :: Windows 10",
    "Environment :: Console",
    "Intended Audience :: Financial and Insurance Industry",
]

setup(
    name = "investingscraper",
    version = "0.0.2",
    description = "Developed by SamedZZZZ",
    long_description = "New features are coming.",
    url = "",
    author = "SamedZZZZ",
    author_email = "zirhlioglusamed@gmail.com",
    license = "MIT",
    classifiers = classifiers,
    keywords = "investing",
    packages = find_packages(),
    install_requires = ["cloudscraper", "pandas"]
)