import setuptools

setuptools.setup(
    name="ifaa",
    version="0.1.0",
    license = 'MIT',
    url="https://github.com/lovestat/ifaa",
    author="Zhigang Li, Quran Wu, Shangchen Song",
    author_email="lzg2151@gmail.com, s.song@ufl.edu",
    description="Robust association identification and inference for absolute abundance in microbiome analyses",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    install_requires=['joblib>=0.10.3', 'numpy>=1.22.3', 'scipy>=1.8.0', 'pandas>=1.4.1', 'glmnet_py', 'matplotlib>=3.5.1', 
                      'tqdm>=4.63.1', 'statsmodels>=0.13.2'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
    include_package_data=True,
    package_data={'': ['data/*.csv']},
)
