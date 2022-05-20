from setuptools import setup

setup(
    name='bayesKMeans',
    version="0.2.0",
    author='Aleksandr Burlakov',
    author_email='samitist11@gmail.com',
    description='Finding optimal k in k-means using bayesian optimization',
    url='https://github.com/ForseIKomar/BayesKMeans',
    install_requires=['joblib>=0.11', 'pyaml>=16.9', 'numpy>=1.13.3',
                      'scipy>=0.19.1',
                      'scikit-learn>=0.20.0', 'scikit-optimize>=0.9.0'],
)
