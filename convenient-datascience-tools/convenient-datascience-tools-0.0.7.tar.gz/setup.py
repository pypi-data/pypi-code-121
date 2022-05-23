import setuptools

from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='convenient-datascience-tools',
    version='0.0.7',
    license='MIT',
    author="Guilherme Turtera",
    author_email='guiturtera@hotmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/guiturtera/convenient-datascience-tools',
    keywords='data science tool',
    install_requires=[
          'pandas',
      ],
    long_description=long_description,
    long_description_content_type='text/markdown'
)