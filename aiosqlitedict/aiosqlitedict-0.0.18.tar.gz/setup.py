import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aiosqlitedict",
    version="0.0.18",
    author="Abdelrahman Sabry",
    author_email="drakth5364@gmail.com",
    description="aiosqlitedict is a Python package that provides easy way to convert from json/dict to sqlite and vise"
                " versa.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sabrysm/aiosqlitedict",
    project_urls={
        "Bug Tracker": "https://github.com/sabrysm/aiosqlitedict/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)