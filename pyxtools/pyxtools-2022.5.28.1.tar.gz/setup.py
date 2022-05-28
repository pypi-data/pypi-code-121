# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# version info
VERSION = (2022, 5, 28, 1)
VERSION_STATUS = ""
VERSION_TEXT = ".".join(str(x) for x in VERSION) + VERSION_STATUS

setup(name="pyxtools",
      version=VERSION_TEXT,
      description="simple tool for Python3.6",
      long_description=open("README.rst", "r").read(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: Other Audience',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Scientific/Engineering',
          'Topic :: Software Development :: Libraries',
          'Topic :: Utilities',
      ],
      install_requires=[
          "requests",
          "chardet",
          "Pillow",
          "opencv-python",
          "numpy",
          "aiohttp",
          "matplotlib",
          "scipy",
      ],
      author="frkhit",
      url="https://github.com/frkhit/pyxtools",
      author_email="frkhit@gmail.com",
      license="MIT",
      packages=find_packages(),
      package_data={'': ["LICENSE", "README.rst", "MANIFEST.in"]},
      include_package_data=True, )
