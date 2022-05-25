import os

from setuptools import setup, find_packages

__version__ = '0.0.dev1653494325'


def read(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return f.read()


setup(
    name='discord-coworking',
    version=__version__,
    author='Ettore Leandro Tognoli',
    author_email='ettoreleandrotognoli@gmail.com',
    license='Apache License 2.0',
    data_files=[
        'LICENSE',
    ],
    description='Discord coworking server management toolkit',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    packages=find_packages(
        './src/main/python/',
    ),
    package_dir={'': 'src/main/python'},
    include_package_data=True,
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
    ],
    python_requires='>=3.6',
    install_requires=[
        'discord.py==1.6.*',
        'emoji==0.6.*',
        'docker==4.4.*',
    ],
    tests_require=[
        'coverage',
        'pylint',
    ],
    entry_points={
        'console_scripts': [
            'discord-coworking=discord_coworking.main'
        ]
    },
)
