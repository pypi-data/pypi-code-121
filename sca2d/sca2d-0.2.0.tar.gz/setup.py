'''Setup for the module'''

__author__ = 'Julian Stirling'
__version__ = '0.2.0'

import sys
from os import path
import glob
from setuptools import setup, find_packages

def install():
    '''The installer'''

    if sys.version_info[0] == 2:
        sys.exit("Sorry, Python 2 is not supported")

    package_data_location = glob.glob('sca2d/lark/*.lark')
    package_data_location = [package[6:] for package in package_data_location]

    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, 'README.md'), encoding='utf-8') as file_id:
        long_description = file_id.read()
    short_description = ('An experimental static code analyser for OpenSCAD.')

    setup(name='sca2d',
          version=__version__,
          license="GPLv3",
          description=short_description,
          long_description=long_description,
          long_description_content_type='text/markdown',
          author=__author__,
          author_email='julian@julianstirling.co.uk',
          packages=find_packages(),
          package_data={'sca2d': package_data_location},
          keywords=['OpenSCAD', 'Linting'],
          zip_safe=False,
          url='https://gitlab.com/bath_open_instrumentation_group/sca2d',
          project_urls={"Bug Tracker": "https://gitlab.com/bath_open_instrumentation_group/sca2d/issues",
                        "Source Code": "https://gitlab.com/bath_open_instrumentation_group/sca2d"},
          classifiers=['Development Status :: 5 - Production/Stable',
                       'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                       'Programming Language :: Python :: 3.6'],
          install_requires=['lark-parser', 'colorama'],
          python_requires=">=3.6",
          entry_points={'console_scripts': ['sca2d = sca2d.__main__:main']})

if __name__ == "__main__":
    install()
