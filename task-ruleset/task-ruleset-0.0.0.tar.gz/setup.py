import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="task-ruleset",
    version="0.0.0",
    description="Test",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/venunathan12/task-ruleset",
    author="Venu Nathan",
    author_email="venunathan12@gmail.com",
    license="MIT",
    classifiers=[],
    packages=["task_ruleset"],
    include_package_data=True,
    install_requires=[],
)