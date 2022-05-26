from distutils.core import setup
from os import path

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, r'README'), encoding='utf-8') as f:
    readme_text = f.read()

# setup function
setup(
    name = 'mydatau',
    packages = ['mydatau'],
    version = '0.0.2',
    license = 'MIT',
    description = 'Expandable module of statistical data utilities',
    long_description=readme_text,
    author = 'econcz',
    author_email = '29724411+econcz@users.noreply.github.com',
    url = 'https://github.com/econcz/mydatau',
    download_url = 'https://github.com/econcz/mydatau/archive/pypi-0_0_2.tar.gz',
    keywords = [
        'statistical data', 'utilities', 'Jupyter', 'R', 'Stata', 'Julia',
        'Octave'
    ],
    install_requires = ['numpy'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
  ],
)