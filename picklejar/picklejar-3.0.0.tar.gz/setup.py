# coding=utf-8
"""Setup script for picklejar Python module"""
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='picklejar',
      version='3.0.0',
      author='Jesse Almanrode',
      author_email='jesse@almanrode.com',
      description='Read and write pickles to a single file',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='GNU Lesser General Public License v3 or later (LGPLv3+)',
      url='http://picklejar.readthedocs.io/',
      py_modules=['picklejar'],
      python_requires='>=3.7',
      install_requires=['dill', ],
      platforms='any',
      classifiers=[
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      )
