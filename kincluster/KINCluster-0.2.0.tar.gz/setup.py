try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from KINCluster import __version__

with open('requirements.txt') as f:
    requires = f.read().splitlines()


setup(
    name = 'KINCluster',
    packages = ['KINCluster' ,'KINCluster/core', 'KINCluster/lib'],
    include_package_data=True,
    version = __version__,
    description = 'Korean Involute News Cluster',
    license = 'MIT',
    author = 'Bae jiun',
    author_email = 'alice.maydev@gmail.com',
    
    url = 'https://github.com/MaybeS/KINCluster',
    keywords = ['KINCluster', 'cluster', 'documents' 'doc2vec', 'tokenize', 'korean'],

    install_requires=requires,

    classifiers=(
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ),

    entry_points={
        'console_scripts': [
            'jikji = jikji.cli:main',
        ],
    },
)
