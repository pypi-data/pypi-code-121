"""
Pypi setup file
"""

from setuptools import setup, find_packages

def load_readme():
    """Load README.md as string"""
    with open('README.md', encoding='utf-8') as inp:
        return inp.read()

setup(
    name='git_dashboard',
    version='0.1.12',
    description="Git dashboard",
    author="Jung Ko",
    author_email="kojung@gmail.com",
    license="GPL",
    platforms=['any'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    python_requires='>=3.6',
    install_requires=[
        "appdirs",
        "GitPython",
        "PySide6",
        "PyYAML",
    ],
    scripts=[
        'bin/git-dashboard',
    ],
    long_description=load_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/kojung/git-dashboard',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
)
