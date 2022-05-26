from pathlib import Path

from setuptools import setup

# read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='apacepy',
    version='1.0.4',
    install_requires=['numpy', 'matplotlib', 'scipy', 'deampy', 'statsmodels', 'sklearn'],
    packages=['apacepy', 'apacepy.analysis'],
    url='https://github.com/yaesoubilab/apacepy',
    license='MIT License',
    author='Reza Yaesoubi',
    author_email='reza.yaesoubi@yale.edu',
    description='Analytical Platform for Adaptive Control of Epidemics (APACE)',
    long_description=long_description,
)
