from setuptools import setup, find_packages
from os import path
import os
import time

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


VERSION = '1.6.7'
if "-" in VERSION: VERSION = VERSION.split("-")[0]
VERSION += "." + str(time.time()).split(".")[0][3:]
DESCRIPTION = 'A package to let your IDE know what JsMacros can do'

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('JsMacrosAC')

# Setting up
setup(
    name="JsMacrosAC",
    version=VERSION,
    author="Hasenzahn1",
    author_email="<motzer10@gmx.de>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=["JsMacrosAC"],
    package_data = {"": extra_files},
    install_requires=[],
    keywords=['python', 'JsMacros', 'Autocomplete', 'Doc'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)