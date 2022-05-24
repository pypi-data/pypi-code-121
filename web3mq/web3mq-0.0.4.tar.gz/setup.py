from os.path import join
from os.path import dirname

from setuptools import find_packages
from setuptools import setup


def read_version():
    version_contents = {}
    with open(join(dirname(__file__), 'web3mq', 'version.py')) as fh:
        exec(fh.read(), version_contents)

    return version_contents['VERSION']


def load_readme():
    return "Web3MQ Python Library"


INSTALL_REQUIRES = [
    "paho-mqtt>=1.6.1",
    "requests>=2.27.1"
]


setup(
    name='web3mq',
    version=read_version(),
    description='Web3MQ Python Library',
    long_description=load_readme(),
    long_description_content_type='text/markdown',
    author='Web3MQ',
    url='https://github.com/Generative-Labs/Web3MQ-SDK-Python',
    license='MIT',
    keywords='Web3MQ python sdk',
    packages=find_packages(
        exclude=[
            'tests',
            'tests.*',
            'testing',
            'testing.*',
            'virtualenv_run',
            'virtualenv_run.*',
        ],
    ),
    zip_safe=False,
    install_requires=INSTALL_REQUIRES,
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)