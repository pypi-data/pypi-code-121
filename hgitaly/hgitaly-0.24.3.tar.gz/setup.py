from pathlib import Path
from setuptools import setup, find_packages

with open('install-requirements.txt', 'r') as install_reqf:
    install_req = [req.strip() for req in install_reqf]

VERSION_FILE = 'VERSION'

setup(
    name='hgitaly',
    version=Path('hgitaly', VERSION_FILE).read_text().strip(),
    author='Georges Racinet',
    author_email='georges.racinet@octobus.net',
    url='https://foss.heptapod.net/heptapod/hgitaly',
    description="Server-side implementation of Gitaly protocol for Mercurial",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords='hg mercurial heptapod gitlab',
    license='GPLv2+',
    packages=find_packages(),
    package_data=dict(hgitaly=[VERSION_FILE]),
    install_requires=install_req,
    python_requires='>=3.8',
)
