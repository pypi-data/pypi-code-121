import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="gs-peer-connection",
    version="0.0.30.2",
    description="python peer connection adapter",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://glass-sphere-ai.de",
    author="Glass Sphere Software",
    author_email="",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["gspeerconnection"],
    include_package_data=True,
    install_requires=["aiortc",
                      "aiohttp",
                      "python-socketio",
                      "crc32c"],
    entry_points={
        "console_scripts": [
            "realpython=gspeerconnection.__main__:main",
        ]
    },
)
