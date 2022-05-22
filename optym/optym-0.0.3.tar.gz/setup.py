from setuptools import setup
from optym import __version__

with open("README.md", "r") as fh:
    readme = fh.read()

setup(
    name="optym",
    version=__version__,
    # url="",
    license="MIT License",
    author="Eduardo M. de Morais",
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email="emdemor415@gmail.com",
    keywords="",
    description=u"Some optimization functions",
    packages=["optym"],
    install_requires=["numpy", "pandas", "setuptools"],
)
