from ctypes.wintypes import LONG
from setuptools import setup, find_packages

VERSION = '1.1.25'
DESCRIPTION = 'A Python library for creating games in the terminal. test'
LONG_DESCRIPTION = open('ReadME.md', 'r').read()

# Setting up
setup(
    name="pyRetroGame",
    version=VERSION,
    author="Lorix & JProgrammer", 
    author_email="<ciminata08@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'consoleGames', 'games', 'terminalGames', 'console', 'terminal', 'game', 'gameEngine', 'gameEngineLibrary', 'gameEngineLibraryPython'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)