import setuptools
import os


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as fp:
        s = fp.read()
    return s


def get_version(path):
    with open(path, "r") as fp:
        lines = fp.read()
    for line in lines.split("\n"):
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name='sentence-embedding-evaluation-german',
    version=get_version("sentence_embedding_evaluation_german/__init__.py"),
    description='Sentence embedding evaluation for German',
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    url='http://github.com/ulf1/sentence-embedding-evaluation-german',
    author='Ulf Hamster',
    author_email='554c46@gmail.com',
    license='Apache License 2.0',
    packages=['sentence_embedding_evaluation_german'],
    install_requires=[
        "torch>=1.1.0,<2",
        "pandas>=1.3.5,<2",
        "scikit-learn>=1.0.2,<2"
    ],
    python_requires='>=3.6',
    zip_safe=True
)
