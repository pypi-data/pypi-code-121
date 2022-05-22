from setuptools import setup

from notes2py.__version__ import __version__

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.readlines()

setup(
    name='Notes2Py',
    version=__version__,
    packages=['notes2py', 'notes2py.ui'],
    license='MIT',
    author='lav.',
    author_email='me@lavn.ml',
    description='PyQt app to manage your notes',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='python pyqt notes',
    url='https://github.com/fast-geek/Notes2Py',
    python_requires='>=3.6.1',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'notes2py = notes2py:main'
        ]
    },
    project_urls={
        "Homepage": "https://github.com/fast-geek/Notes2Py",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
