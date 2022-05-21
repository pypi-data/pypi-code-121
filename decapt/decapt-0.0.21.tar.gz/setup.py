from setuptools import setup
from pathlib import Path

GEN_version = "0.0.21"
READ_name = "decapt"

here = Path(__file__).parent.resolve()

setup(
    name=READ_name,
    version=GEN_version,
    author="rendaw",
    url="https://gitlab.com/rendaw/decapt",
    download_url="https://gitlab.com/rendaw/decapt/-/archive/v{v}/decapt-v{v}.tar.gz".format(
        v=GEN_version
    ),
    license="MIT",
    description="Arch Linux declarative package management",
    long_description=(here / "README.md").read_text(),
    long_description_content_type="text/markdown",
    classifiers=[],
    packages=["decapt"],
    install_requires=["luxem==0.0.2",],
    entry_points={"console_scripts": ["decapt=decapt.main:main",],},
)
