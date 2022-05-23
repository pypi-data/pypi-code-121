#!/usr/bin/python3

from distutils.core import setup

setup(
    name='ada_assistant',
    version='1.2.0',
    description='Ada: cmd helper that does lot of things',
    long_description='To be added when author is free...',
    long_description_content_type='text/x-rst',
    author='yuquanshan',
    license='MIT',
    packages = ['ada'],
    install_requires=[
        'pycrypto',
    ],
    python_requires='>=3',
    package_data={'ada': ['data/*.dat', 'data/*.txt']},
    entry_points={
        'console_scripts': [
            'ada=ada.main:main',
        ]
    },
)
