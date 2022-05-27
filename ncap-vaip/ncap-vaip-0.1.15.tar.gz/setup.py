"""
This setup.py file sets the configuration and builds this Python package. This makes
it available for imports and script running without needing a local copy

(c) NCEI's National Centers for Environmental Information
"""

import os
import shutil
import sys

from setuptools import setup, find_packages

# Insert arbitrary build task options/code here
print(sys.argv[-1])
if sys.argv[-1] == 'clean':
    if os.path.exists('../vaip.egg-info'):
        shutil.rmtree('../vaip.egg-info')
    if os.path.exists('dist'):
        shutil.rmtree('dist')

# Set up
# scripts_path = os.path.join(os.path.dirname('__file__'), 'scripts')
setup(
    name='ncap-vaip',
    version='0.1.15',
    url='https://www.noaa.gov',
    author='NCAP Team',
    author_email='ncap.support@noaa.gov',
    license='GPLv2',
    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-html'],
    install_requires=['requests',
                      'rdflib>=6.1.1',
                      'yurl'
                      ],
    package_data={
        '': ['data/*.owl'],
    },
    include_package_data=True
)


