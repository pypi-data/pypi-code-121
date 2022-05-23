from pathlib import Path
from setuptools import setup

with open("README.md", "r") as fs:
    long_description = fs.read()

with open("version", "r") as fs:
    version = fs.read()

setup(
    name="ModFixer",
    version=version,
    author="ArchLeaders",
    author_email="archleadership28@gmail.com",
    description="CLI for on the fly GFX packing to load as a Cemu graphic pack for quick and efficient testing.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArchLeaders/ModFixer",
    include_package_data=True,
    packages=["modfixer"],
    package_dir={"modfixer": "modfixer"},
    entry_points={
        "console_scripts": [
            "modfixer = modfixer.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
    ],
    python_requires=">=3.7",
    install_requires=Path("requirements.txt").read_text().splitlines(),
    zip_safe=False,
)
