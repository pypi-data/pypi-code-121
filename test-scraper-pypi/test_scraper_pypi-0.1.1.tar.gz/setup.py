#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Kishore Sampath",
    author_email='skishore2602.dev@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Testing scraper package as pip package",
    entry_points={
        'console_scripts': [
            'test_scraper_pypi=test_scraper_pypi.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='test_scraper_pypi',
    name='test_scraper_pypi',
    packages=find_packages(include=['test_scraper_pypi', 'test_scraper_pypi.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/kishore-s-15/test_scraper_pypi',
    version='0.1.1',
    zip_safe=False,
)
