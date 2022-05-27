from setuptools import setup


with open('PACKAGE_README.md', 'r') as readme_file:
    long_description = readme_file.read()
VERSION = '2.9.5'


setup(
    name='randword',
    description='A Python package for generation random English words',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=[
        'python', 'package', 'python-package', 'random',
        'word', 'words', 'generator', 'generation',
        'random-word', 'random-words', 'random-word-generator',
        'random-word-generation', 'english',
        'english-word', 'english-words'
    ],
    version=VERSION,

    author='Artyom Bezmenov (8nhuman)',
    author_email='artem.bezmenov02@gmail.com',
    license='MIT',

    packages=['randword'],
    include_package_data=True,

    project_urls={
        'Bug Tracker': 'https://github.com/8nhuman8/randword/issues',
        'Source Code': 'https://github.com/8nhuman8/randword',
        'Documentation': 'https://randword.readthedocs.io/en/stable/',
        'Download': f'https://github.com/8nhuman8/randword/archive/{VERSION}.tar.gz',
        'Homepage': 'https://github.com/8nhuman8/randword'
    },

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent'
    ]
)
