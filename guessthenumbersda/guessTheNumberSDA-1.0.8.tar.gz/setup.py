from setuptools import setup, find_packages
import codecs
import os


VERSION = '1.0.8'
DESCRIPTION = 'Guess the name game. Play to win!'

# Setting up
setup(
    name="guessTheNumberSDA",
    version=VERSION,
    author="Guido Xhindoli",
    author_email="<mail@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[],
    keywords=['pythonal', 'pythonal7', 'game', 'sda', 'guess'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)