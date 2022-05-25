# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os 

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
    
setup(
    name='simcap',
    description='Simulation of Correlated Asset Prices',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.2.0',
    author='Jeremy Doyle',
    author_email='hello@jeremy-doyle.com',
    url='https://github.com/jeremy-doyle/simcap',
    license='MIT',
    install_requires=[
        'numpy>=1.17',
        'scipy>=1.3',
        'statsmodels>=0.13.0',
        'scikit-learn>=0.18',
        'hmmlearn>=0.2.7',
        'pandas>=1.0',
        'tqdm',
    ],
    tests_require=['pytest'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords=[
        'finance',
        'investment',
        'analysis',
        'securities',
        'simulation',
        'markov',
        'time',
        'series',
        'monte',
        'carlo',
        'risk',
        ],
    packages=find_packages(exclude=['tests*','examples*,docs*']),
    package_data={'simcap': ['datasets/csv/*.csv']},
    python_requires='>=3.7',
)