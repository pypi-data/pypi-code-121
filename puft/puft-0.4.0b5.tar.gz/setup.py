import pathlib
from setuptools import setup, find_packages

from puft import __version__ as version


here = pathlib.Path(__file__).parent.resolve()

with open("requirements.txt", "r") as file:
    install_requires = [x.strip() for x in file.readlines()]

setup(
    name="puft",
    version=version,
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description="Upgraded layer over Flask.",
    author="Alexander Ryzhov",
    author_email="thed4rkof@gmail.com",
    url="https://github.com/ryzhovalex/puft",
    keywords=["flask+", "web-framework", "flask", "flask-template"],
    entry_points={
        "console_scripts": [
            "puft = puft.tools.cli:main",
        ],
    },
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",

        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3.10",
    ],
)
