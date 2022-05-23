import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="pypomodoro",
    version="0.7.0",
    description="Displays a full screen pomodoro timer in the terminal",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/lostways/pypomodoro",
    author="Andrew Lowe",
    author_email="andrew@lostways.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    entry_points = {
      'console_scripts': ['pypomodoro=pypomodoro.main:main']
    },
)

