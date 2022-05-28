import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="diagnscls",
    version="0.0.2", 
    author="Mingyu Choi",
    author_email="cmg5691@gmail.com",
    description="diagnosis for non-small cell lung cancer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cheymingyu/Biomarker",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)