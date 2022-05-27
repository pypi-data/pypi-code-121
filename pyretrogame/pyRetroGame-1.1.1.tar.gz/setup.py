from setuptools import setup, find_packages

VERSION = '1.1.1'
DESCRIPTION = 'A Python library for creating games in the terminal. test'

# Setting up
setup(
    name="pyRetroGame",
    version=VERSION,
    author="Lorix & JProgrammer",
    author_email="<ciminata08@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['os', 'curses', 'time', 'threading'],
    keywords=['python', 'consoleGames', 'games', 'terminalGames', 'console', 'terminal', 'game', 'gameEngine', 'gameEngineLibrary', 'gameEngineLibraryPython'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)