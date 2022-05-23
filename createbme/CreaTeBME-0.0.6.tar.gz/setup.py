import setuptools
from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='CreaTeBME',
    version='0.0.6',
    author='Jonathan Matarazzi',
    author_email='dev@jonathanm.nl',
    description='Python Package for interfacing the bluetooth IMU module for CreaTe M8 BME.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/CreaTe-M8-BME/CreaTeBME',
    project_urls={
        'Bug Tracker': 'https://github.com/CreaTe-M8-BME/CreaTeBME/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent'
    ],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    python_requires='>=3.6',
    install_requires=[
        'pyserial >= 3.5',
        'pybluez == 0.22',
        'prompt_toolkit >= 3.0.29',
    ]
)
