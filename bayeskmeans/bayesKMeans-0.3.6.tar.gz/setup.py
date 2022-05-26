"""
Библиотека байесовской оптимизации позволяет определить количество кластеров в наборе данных с использованием
алгоритма k-средних

Aleksandr Burlakov
samitist11@gmail.com
"""

from setuptools import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='bayesKMeans',
    version="0.3.6",
    author='Aleksandr Burlakov',
    author_email='samitist11@gmail.com',
    description='Finding optimal k in k-means using bayesian optimization',
    long_description=long_description,
    url='https://github.com/ForseIKomar/BayesKMeans',
    install_requires=['joblib>=0.11', 'pyaml>=16.9', 'numpy>=1.13.3',
                      'scipy>=0.19.1',
                      'scikit-learn>=0.20.0', 'scikit-optimize>=0.9.0'],
)
