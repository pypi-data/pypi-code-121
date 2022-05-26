import os
from setuptools import setup, find_packages

lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_file = 'requirements.txt'
full_path = '/'.join([lib_folder, requirement_file])

install_requires = []
if os.path.isfile(full_path):
    with open(full_path) as f:
        install_requires = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='rr-api-beta',
      version='1.3',
      description='rr-api',
      url='https://upload.pypi.org/legacy/',
      author='RR Team',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author_email='rr@rr.com',
      license='MIT',
      install_requires=install_requires,
      packages=find_packages(),
      zip_safe=False,
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.10',
      )
