from pathlib import Path

from setuptools import setup

# read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='deampy',
    version='1.0.15',
    install_requires=['numpy', 'matplotlib', 'scipy', 'statsmodels', 'sklearn'],
    packages=['deampy', 'deampy.optimization', 'deampy.plots', 'deampy.support'],
    url='https://github.com/modeling-health-care-decisions/deampy',
    license='MIT License',
    author='Reza Yaesoubi',
    author_email='reza.yaesoubi@yale.edu',
    description='Decision analysis in medicine and public health',
    long_description=long_description
)
