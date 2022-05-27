from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

VERSION = '0.0.1'
DESCRIPTION = 'BeatifulColorText'
LONG_DESCRIPTION = 'A package that make your code beatiful :)'

# Setting up
setup(
    name="bct",
    version=VERSION,
    author="Xin1337 & ZayDev",
    author_email="<xin1337dev@protonmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['colored'],
    keywords=['python', 'tui', 'terminal', 'user', 'interface', 'color', 'animation'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
