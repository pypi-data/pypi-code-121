from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name = 'homeman',
    version = '1.0.3',
    description = 'keep files synchronized between user home and your special home directory',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitee.com/sunn4open/homeman.git',
    author = 'sunn4room',
    author_email = 'sunn4room@163.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages = find_packages(),
    install_requires = ['colorama'],
    entry_points = {
        'console_scripts': [
            'homeman = homeman:main'
        ]
    }
)
