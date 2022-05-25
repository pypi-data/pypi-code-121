from setuptools import setup

setup(
    name='deampy',
    version='1.0.14',
    install_requires=['numpy', 'matplotlib', 'scipy', 'statsmodels', 'sklearn'],
    packages=['deampy', 'deampy.optimization', 'deampy.plots', 'deampy.support'],
    url='https://github.com/modeling-health-care-decisions/deampy',
    license='MIT License',
    author='Reza Yaesoubi',
    author_email='reza.yaesoubi@yale.edu',
    description='Decision analysis in medicine and public health'
)
