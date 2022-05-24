from setuptools import setup


setup(
    name="lxcommon",
    author="Luís Gomes",
    author_email="luis.gomes@di.fc.ul.pt",
    version="2.13.5",
    description="LX-Common is a package for code bits shared across several LX tools.",
    package_dir={"": "src"},
    packages=["lxcommon"],
)
