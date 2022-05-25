import os

from setuptools import find_packages, setup

from file_writer_control._version import version

DESCRIPTION = (
    "A small Python library for controlling the ESS kafka-to-nexus file-writer."
)

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
try:
    with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        LONG_DESCRIPTION = "\n" + f.read()
except Exception as error:
    print("COULD NOT GET LONG DESC: {}".format(error))
    LONG_DESCRIPTION = DESCRIPTION

setup(
    name="file_writer_control",
    version=version,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="ScreamingUdder",
    url="https://github.com/ess-dmsc/file_writer_control",
    license="BSD 2-Clause License",
    packages=find_packages(exclude=["tests", "examples"]),
    entry_points={
        "console_scripts": [
            "start_file_writer = cli.start_file_writer:start_writer",
            "stop_file_writer = cli.stop_file_writer:stop_writer",
        ],
    },
    python_requires=">=3.6.0",
    install_requires=["kafka-python>=2.0", "ess-streaming-data-types>=0.14.0"],
)
