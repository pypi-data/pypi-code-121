from setuptools import find_packages,setup
from xes import version
setup(
    name = 'xes-lib',
    version = version.version,
    author = 'xes',
    description = '学而思库',
    packages = find_packages(),
    install_requires = ["requests", "pypinyin", "pygame"],
    url = 'https://code.xueersi.com'
)