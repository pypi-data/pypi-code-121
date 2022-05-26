from setuptools import setup

setup(
    name='apacepy',
    version='1.0.2',
    install_requires=['numpy', 'matplotlib', 'scipy', 'deampy', 'statsmodels', 'sklearn'],
    packages=['apacepy', 'apacepy.analysis'],
    url='https://github.com/yaesoubilab/apacepy',
    license='MIT License',
    author='Reza Yaesoubi',
    author_email='reza.yaesoubi@yale.edu',
    description='Analytical Platform for Adaptive Control of Epidemics (APACE)',
    long_description='file: README.md',
)
