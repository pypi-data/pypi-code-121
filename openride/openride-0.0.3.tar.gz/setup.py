from setuptools import setup

with open("README.md", 'r') as file:
    long_description = file.read()

requirements = [
    'shapely',
    'numba',
    'numpy',
    'dataclasses',
    'vtk',
    'matplotlib',
]

setup(name = 'openride',
      version = '0.0.3',
      author = 'Jean-Luc Déziel',
      author_email = 'jluc1011@hotmail.com',
      url = 'https://gitlab.com/jldez/openride',
      description = '',
      long_description = long_description,
      long_description_content_type = 'text/markdown',
      packages = [
          'openride',
          'openride.core',
          'openride.viewer',
          'openride.examples',
      ],
      install_requires = requirements,
    )