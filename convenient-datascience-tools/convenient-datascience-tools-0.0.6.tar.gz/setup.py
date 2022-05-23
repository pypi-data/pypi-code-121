import setuptools

from setuptools import setup, find_packages


setup(
    name='convenient-datascience-tools',
    version='0.0.6',
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

)