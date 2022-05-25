import setuptools
from docparser import __version__

setuptools.setup(
    name='CoDocParser',
    version=__version__,
    packages=setuptools.find_packages("."),  # I also tried exclude=["src/test"]
    url='https://www.cityocean.com',
    license='GPL',
    author='CityOcean',
    author_email='it@cityocean.com',
    description='文档解析器',
    keywords=['document', 'parser'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*",
    extras_require=dict(
        build=['wheel', 'twine']
    ),
    install_requires=[
        'pdfminer', 'marshmallow', 'lxml', 'pandas', 'numpy', 'parse','chardet'
    ],
)
