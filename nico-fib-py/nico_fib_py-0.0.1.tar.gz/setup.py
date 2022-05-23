from importlib.metadata import entry_points
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="nico_fib_py",
    version="0.0.1",
    author="NK",
    author_email="nicolas.kateb@yahoo.fr",
    description="Calculates a Fibonacci number",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nicolask-perso/nico-fib.git",
    install_requires=[],
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