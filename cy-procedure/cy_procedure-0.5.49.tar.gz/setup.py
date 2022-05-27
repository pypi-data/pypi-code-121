#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

requirements = ['Click>=7.0', ] + required

setup_requirements = []

test_requirements = []

setup(
    author="CY Gatro",
    author_email='cragodn@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Procedures based on components/widgets/dao",
    entry_points={
        'console_scripts': [
            'cybnc=cy_procedure.bnc_cli:cybnc',
            'cyok=cy_procedure.ok_cli:cyok',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='cy_procedure',
    name='cy_procedure',
    packages=find_packages(include=['cy_procedure', 'cy_procedure.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/cragod/CYProcedure',
    version='0.5.49',
    zip_safe=False,
)
