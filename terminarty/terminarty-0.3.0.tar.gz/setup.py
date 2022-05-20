from setuptools import setup, find_packages

VERSION = '0.3.0'
DESCRIPTION = 'A simple CLI helper for python'

# Setting up
setup(
    name='terminarty',
    version=VERSION,
    description=DESCRIPTION,
    long_description_content_type='text/markdown',
    long_description='Check '
                     '[GitHub repository](https://github.com/Artemon121/terminarty)'
                     ' for more information',
    packages=find_packages(),
    install_requires=['colorama'],
    keywords=['terminal', 'cli', 'command-line', 'python', 'colored', 'progress bar'],
    author='Artemon121',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ]
)
