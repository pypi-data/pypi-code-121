from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.33'
DESCRIPTION = 'Heroku Utils'
LONG_DESCRIPTION = 'Heroku Utils'

# Setting up
setup(
    name="rupineHeroku",
    version=VERSION,
    author="RupineLabs",
    author_email="<abc@def.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['psycopg2','numpy','python-dotenv','pytz','requests'],
    keywords=['web3'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)