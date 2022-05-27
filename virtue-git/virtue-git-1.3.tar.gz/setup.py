from setuptools import setup, find_packages

setup(
    name = 'virtue-git',
    version = '1.3',
    description = 'Gather information about a GitHub account',
    author = 'Surtains',
    author_email = "surtains@riseup.net",
    url = 'https://github.com/drooling/virtue',
    license = 'GNU General Public License v3 (GPLv3)',
    classifiers = [
        'Programming Language :: Python :: 3.9',
    ],
    packages = find_packages(),
    install_requires = ['httpx', 'trio'],
    entry_points = {'console_scripts': ['virtue = virtue.core:main']}
)