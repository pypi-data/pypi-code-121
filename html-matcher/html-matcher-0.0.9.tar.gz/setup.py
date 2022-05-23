from setuptools import setup, find_packages
from pathlib import Path

VERSION = '0.0.9'
DESCRIPTION = 'Algorithms to find similarity between HTML pages.'
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Setting up
setup(
    name="html-matcher",
    version=VERSION,
    author="Pedro Carvalho",
    author_email="<pedrocarvalho812@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    url='https://github.com/officialpedrocarvalho/html-matcher',
    download_url='https://github.com/officialpedrocarvalho/html-matcher/releases/tag/version',
    install_requires=['XlsxWriter', 'parsel', 'lxml', 'apted'],
    keywords=['python', 'website', 'webapp', 'html', 'similarity', 'match', 'rate'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License"
    ]
)
