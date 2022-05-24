#!/usr/bin/python3
from setuptools import setup, find_packages
# Package meta-data, mostly from the package
from kibot import __author__, __email__, __url__, __version__, __pypi_deps__

# Use the README.md as a long description.
# Note this is also included in the MANIFEST.in
with open('README.md', encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(name='kibot',
      version=__version__,
      description='KiCad automation tool for documents generation',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author=__author__,
      author_email=__email__,
      url=__url__,
      # Packages are marked using __init__.py
      packages=find_packages(),
      scripts=['src/kibot', 'src/kiplot', 'src/kibot-check'],
      install_requires=__pypi_deps__,
      include_package_data=True,
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                   'Natural Language :: English',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 3',
                   'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
                   ],
      platforms='POSIX',
      license='GPL-3.0',
      python_requires='>=3.6',
      )
