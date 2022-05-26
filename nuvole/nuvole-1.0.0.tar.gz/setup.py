from setuptools import setup
from pathlib import Path


setup(
    name='nuvole',
    version='1.0.0',
    packages=['nuvole'],
    url='https://github.com/crogeo/nuvole',
    license='MIT License',
    author='crogeo.org',
    author_email='c.crogeo@gmail.com',
    description='Simple wrapper of Python tornado web framework',
    long_description=Path('README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    install_requires=['tornado']
)
