from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name = 'virtue-git',
    version = '1.3.2',
    description = 'Gather information about a GitHub account',
    author = 'Surtains',
    author_email = "surtains@riseup.net",
    url = 'https://github.com/drooling/virtue',
    license = 'GNU General Public License v3 (GPLv3)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Source": "https://github.com/drooling/virtue",
    },
    classifiers = [
        'Programming Language :: Python :: 3.9',
    ],
    packages = find_packages(),
    install_requires = ['httpx', 'trio'],
    entry_points = {'console_scripts': ['virtue = virtue.core:main']}
)