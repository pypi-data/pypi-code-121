from importlib.metadata import entry_points
from importlib_metadata import version
from setuptools import find_packages, setup
import pathlib

with open("README.md", "r") as fh:
    long_description = fh.read()

with open(str(pathlib.Path(__file__).parent.absolute()) + "/nico_fib_py/version.py", "r") as fh:
    version=fh.read().split("=")[1].replace("'","")


setup(
    name="nico_fib_py",
    version=version,
    author="NK",
    author_email="nicolas.kateb@yahoo.fr",
    description="Calculates a Fibonacci number",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nicolask-perso/nico-fib.git",
    install_requires=[
        "PyYAML>=4.1.2",
        "dill>=0.2.8"
    ],
    extras_require={
        'server': ["Flask>=1.0.0"]
    },
    packages=find_packages(exclude=("tests")),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'fib-number = nico_fib_py.cmd.fib_number:fib_numb',
        ],
    },
    python_requires='>=3',
    tests_require=['pytest'],
)