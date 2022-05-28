from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

VERSION = '0.1'
DESCRIPTION = 'The bridge between code and your telegram messages.'
LONG_DESCRIPTION = 'A package that allows you simple communication with your telegram app.'

# Setting up
setup(
    name="yoo-telegram",
    version=VERSION,
    author="William Brach",
    author_email="<wibrach@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['python', 'telegram', 'notifications', 'notifier', 'bot'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)