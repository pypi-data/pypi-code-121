from setuptools import find_packages, setup

setup(
    name='metathing',
    version='0.1.17',
    description='MT-Service Python',
    license='N/A',
    packages=find_packages(
        exclude=['test', 'workdir', 'metathing/__pycache__']),
)
