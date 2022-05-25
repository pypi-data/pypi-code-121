import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hyphon-ihak223",
    version="0.0.5",
    author="ihak223",
    description="-",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ihak223/hyphon",
    project_urls={
        "Bug Tracker": "https://github.com/ihak223/hyphon/issues",
    },
    package_dir={"": "src_py"},
    packages=setuptools.find_packages(where="src_py"),
    python_requires=">=3.6",
)