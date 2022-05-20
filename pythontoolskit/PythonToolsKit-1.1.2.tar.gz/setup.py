from platform import system
import PythonToolsKit as package
from subprocess import check_call, DEVNULL
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install


def set_terminal_registry():
    if system() == "Windows":
        from winreg import (
            CreateKey,
            OpenKey,
            SetValueEx,
            CloseKey,
            HKEY_CURRENT_USER,
            KEY_WRITE,
            REG_DWORD,
        )

        PATH = "Console"
        CreateKey(HKEY_CURRENT_USER, PATH)
        key = OpenKey(HKEY_CURRENT_USER, PATH, 0, KEY_WRITE)
        SetValueEx(key, "VirtualTerminalLevel", 0, REG_DWORD, 1)
        CloseKey(key)


class PostDevelopScript(develop):
    def run(self):
        set_terminal_registry()
        develop.run(self)


class PostInstallScript(install):
    def run(self):
        set_terminal_registry()
        install.run(self)


setup(
    name=package.__name__,
    version=package.__version__,
    packages=find_packages(include=[package.__name__]),
    install_requires=[],
    author=package.__author__,
    author_email=package.__author_email__,
    maintainer=package.__maintainer__,
    maintainer_email=package.__maintainer_email__,
    description=package.__description__,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url=package.__url__,
    project_urls={
        "Documentation Timeout": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Timeout.html",
        "Documentation Terminal": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Terminal.html",
        "Documentation StringF": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/StringF.html",
        "Documentation PrintF": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/PrintF.html",
        "Documentation Process": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Process.html",
        "Documentation Logs": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Logs.html",
        "Documentation GetPass": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/GetPass.html",
        "Documentation Encodings": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Encodings.html",
        "Documentation DictObject": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/DictObject.html",
        "Documentation Report": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Report.html",
        "Documentation urlopen": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/urlopen.html",
        "Documentation Dict": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Dict.html",
        "Documentation Tuple": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Tuple.html",
        "Documentation List": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/List.html",
        "Documentation Function": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Function.html",
        "Documentation Arguments": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Arguments.html",
        "Documentation Thread": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Thread.html",
        "Documentation Import": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Import.html",
        "Documentation ScapyTools": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/ScapyTools.html",
        "Documentation GetFile": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/GetFile.html",
        "Documentation GetType": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/GetType.html",
        "Documentation Random": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Random.html",
        "Documentation Json": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Json.html",
        "Documentation WindowsTerminal": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/WindowsTerminal.html",
        "Documentation Colors": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Colors.html",
        "Documentation DataAnalysis": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/DataAnalysis.html",
    },
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.6",
    keywords=[
        "Timeout",
        "Terminal",
        "Colors",
        "Formatting",
        "Print",
        "Object",
        "Process",
        "CSV",
        "Logs",
        "Getpass",
        "Password",
        "Ask",
        "*",
        "Encodings",
        "Report",
        "Markdown",
        "HTML",
        "JSON",
        "Arguments",
        "Input",
        "Output",
        "Operator",
        "List",
        "Tuple",
        "Dict",
        "Function",
        "Statistic",
    ],
    platforms=["Windows", "Linux", "MacOS"],
    license=package.__license__,
    cmdclass={
        "develop": PostDevelopScript,
        "install": PostInstallScript,
    },
)
