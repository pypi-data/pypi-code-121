import os
from setuptools import setup

__version__ = '0.01.02'


def read(f_name):
    return open(os.path.join(os.path.dirname(__file__), f_name)).read()


setup(
    name='hicml',
    version=__version__,
    author='Muhammad Shamim, Alyssa Blackburn, Dimos Gkountaroulis',
    author_email='aidenlab@bcm.edu',
    license='MIT',
    keywords=['Hi-C', '3D genomics', 'Chromatin', 'ML'],
    url='https://github.com/dgound/hic-ml',
    description='ML tools for analyzing Hi-C data',
    long_description=read('README.md'),
    packages=['hicml'],
    install_requires=['numpy', 'scipy', 'keras', 'tensorflow', 'hic-straw'],
    setup_requires=['numpy', 'scipy', 'keras', 'tensorflow', 'hic-straw'],
    python_requires='>3.3',
    zip_safe=False,
)
