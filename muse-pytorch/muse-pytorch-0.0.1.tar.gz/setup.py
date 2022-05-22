import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="muse-pytorch",
    version="0.0.1",
    author="Nicola Occelli",
    author_email="nicola.occelli@ulb.be",
    description="Pytorch version of MUSE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nico995/MUSE-pytorch",
    project_urls={
        "Bug Tracker": "https://github.com/Nico995/MUSE-pytorch/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: GPU :: NVIDIA CUDA :: 10.2",
        "Natural Language :: English",
    ],
    package_dir={"": "muse_pytorch"},
    packages=setuptools.find_packages(where="muse_pytorch"),
    python_requires=">=3.6",
)
