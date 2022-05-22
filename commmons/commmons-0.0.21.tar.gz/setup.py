import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="commmons",
    version="0.0.21",
    author="Jaeseo Park",
    description="pydash + more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaeseopark/commmons",
    packages=setuptools.find_packages(exclude=("test",)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=["requests", "lxml", "pydash"]
)
