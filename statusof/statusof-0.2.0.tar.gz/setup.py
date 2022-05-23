import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="statusof",
    version="0.2.0",
    description="Small python script to check the status of a list of urls.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/arthurdw/statusof",
    author="Arthurdw",
    author_email="dev@arthurdw.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    packages=["statusof"],
    include_package_data=True,
    install_requires=["aiohttp", "colorama"],
    entry_points={
        "console_scripts": [
            "statusof=statusof.__main__:main",
        ]
    },
)
