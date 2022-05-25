import pathlib
from setuptools import setup

PWD = pathlib.Path(__file__).parent

# The text of the README file
README = (PWD / "README.md").read_text()

setup(
    name='coding-FOOBAR_20220520.1',
    packages=['bar'],
    description='requires python >= 3.7',
    long_description=README,
    long_description_content_type='text/markdown',
    version='1.0.1',
    license='MIT',
    python_requires='>=3.8',
    author='coding',
    author_email='coding@coding.com',
    url='https://e.coding.net/codingcorp/coding-artifacts-demo.git',
    download_url='https://codingcorp.coding.net/p/mayday/artifacts/297/pypi/package/471/version/5772',
    keywords=['PyPI', 'artifacts', 'Python']
)
