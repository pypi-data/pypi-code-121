import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="smilepngquant",
    version="1.1.0",
    author="Sitthykun LY",
    author_email="ly.sitthykun@gmail.com",
    description="That is a bridge of pngquant for python3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sitthykun/smilepngquant",
    project_urls={
        "Bug Tracker": "https://github.com/sitthykun/smilepngquant/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.5",
)
