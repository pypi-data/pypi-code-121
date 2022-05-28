import setuptools
from distutils.core import setup
from directory_observer import __version__

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='directory_observer',
    version=__version__,
    description=long_description.split('\n')[1],
    author='ChsHub',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChsHub/directory_observer",
    packages=['directory_observer'],
    license='MIT License',
    classifiers=['Programming Language :: Python :: 3', 'Topic :: Software Development', 'Topic :: Utilities']
)
# C:\Python38\python.exe setup.py sdist bdist_wheel
# C:\Python38\python.exe -m twine upload dist/*
