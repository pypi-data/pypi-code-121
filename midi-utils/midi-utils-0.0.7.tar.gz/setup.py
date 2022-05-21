from setuptools import setup, find_packages


config = {
    "name": "midi-utils",
    "version": "0.0.7",
    "packages": find_packages(),
    "test_requires": [
        "pytest",
    ],
    "author": "Brian Abelson",
    "author_email": "hey@gltd.email",
    "description": "midi-utils provides a couple of simple tools to generate midi notes in different scales",
    "url": "https://gitlab.com/gltd/midi-utils",
}

setup(**config)
