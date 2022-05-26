import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyXor",
    version="1.0.2",
    author="LeRatGondin",
    author_email="leratgondin1@gmail.com",
    description="A xor encryption module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LeRatGondin/PyXor",
    project_urls={
        "Bug Tracker": "https://github.com/LeRatGondin/PyXor/issues",
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