from ensurepip import version
from setuptools import find_packages, setup


def read_requirements(file_name):
    with open(file_name, 'r', encoding='utf8') as f:
        requirements = []
        for line in f:
            requirements.append(line.split('==')[0])
    return requirements
    

setup(
    name="qrutils",
    version="0.0.2",
    author='VictorT',
    packages=find_packages(),
    install_requires=read_requirements('requirements.txt'),
    classifiers=[
        'Programming Language :: Python :: 3.8',
    ]
)
