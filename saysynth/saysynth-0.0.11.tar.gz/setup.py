from setuptools import setup, find_packages

config = {
    "name": "saysynth",
    "version": "0.0.11",
    "packages": find_packages(),
    "install_requires": ["charset-normalizer", "click", "mido", "midi-utils"],
    "author": "Brian Abelson",
    "author_email": "hey@gltd.email",
    "description": "A musical generator for say",
    "url": "http://globally.ltd",
    "entry_points": {
        "console_scripts": ["saysynth=saysynth.cli:main", "sy=saysynth.cli:main"]
    },
}

setup(**config)
