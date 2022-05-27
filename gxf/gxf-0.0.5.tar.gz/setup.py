from setuptools import setup
from setuptools import find_packages

from src.gxf import __author__, __email__, __version__

with open('README.md', 'r', encoding='utf-8') as fp:
    readme = fp.read()

setup(
    name='gxf',
    version=__version__,
    author=__author__,
    author_email=__email__,
    maintainer=__author__,
    maintainer_email=__email__,
    description='A fast gtf/gff parser.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/dwpeng/gxf',
    keywords=['GFF', 'GTF'],
    packages=find_packages('src'),
    package_dir={"": "src"},
    install_requires=[
        'pandas',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ]
)
