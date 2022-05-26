import setuptools

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="vblocks",
    version="0.0.1",
    author="Spencer Neveux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["vblocks"],
)
