from setuptools import setup, find_packages

setup(
    name='geodbpyclient',
    version='1.1.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='Python package for a university course',
    long_description=open('README.md').read(),
    install_requires=['requests'],
    url='https://git.e-science.pl/kwazny_252716_dpp/kwazny252716_dpp_python_pip',
    author='Karol Ważny',
    author_email='kwazny_252716@e-science.pl'
)