from setuptools import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='herolabsapi',
    version='0.3.2',
    packages=['herolabsapi'],
    url='https://github.com/markvader/herolabsapi',
    license='MIT',
    author='Mark Breen',
    author_email='markjbreen@gmail.com',
    description='Python Library for Hero Labs API, creators of the Sonic smart water shut off valve',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
