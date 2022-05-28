from setuptools import setup, find_packages

VERSION = '0.7.0'
DESCRIPTION = 'Machine Learning project startup utilities'
LONG_DESCRIPTION = 'My commonly used utilities for machine learning projects'

setup(
    name='stefutils',
    version=VERSION,
    license='MIT',
    author='Yuzhao Stefan Heng',
    author_email='stefan.hg@outlook.com',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url='https://github.com/StefanHeng/stef-util',
    download_url='https://github.com/StefanHeng/stef-util/archive/refs/tags/0.7.0.tar.gz',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'sty', 'colorama', 'pygments',
        'numpy', 'pandas', 'torch', 'transformers',
        'matplotlib', 'seaborn',
        'tqdm'
    ],
    keywords=['python', 'nlp', 'machine-learning', 'deep-learning'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: MacOS X',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ]
)
