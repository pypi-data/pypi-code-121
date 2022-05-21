import setuptools

from oncoplot_versioneer import OncoplotVersioneer

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

version = OncoplotVersioneer().meta_version()

setuptools.setup(
    name="oncoplot_extractor",
    version=version,
    packages=setuptools.find_packages(),
    url="https://github.com/regmibijay/oncoplot-extractor",
    license="GNU (GPLv3)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Bijay Regmi",
    author_email="oncoplot-extractor@regdelivery.de",
    description="General Toolkit for OncoPlot written in Python",
    install_requires=requirements,
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
