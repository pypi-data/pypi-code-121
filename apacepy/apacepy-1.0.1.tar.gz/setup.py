from setuptools import setup

setup(
    name='apacepy',
    version='1.0.1',
    install_requires=['numpy', 'matplotlib', 'scipy', 'deampy', 'statsmodels', 'sklearn'],
    packages=['apacepy', 'apacepy.analysis'],
    url='https://github.com/yaesoubilab/apacepy',
    license='MIT License',
    author='Reza Yaesoubi',
    author_email='reza.yaesoubi@yale.edu',
    description='Analytical platform for adaptive control of epidemics'
)
