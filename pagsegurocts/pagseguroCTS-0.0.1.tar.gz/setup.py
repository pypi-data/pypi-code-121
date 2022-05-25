from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(name='pagseguroCTS',
    version='0.0.1',
    license='MIT License',
    author='SDK_PS',
    url='https://pypi.org/project/pagseguro/',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='leopoldo.bernardes@monetizze.com.br',
    keywords='pagseguro',
    description=u'SDK pagseguro',
    packages=['pagseguroCTS'],)
