from setuptools import find_packages, setup

# Load README file
with open(file="README.md", mode="r") as readme_handle:
    long_description = readme_handle.read()

setup(
    name="image_caption_generator_elizastarr",
    packages=find_packages(exclude=("tests",)),
    version="0.2.0",
    description="An LSTM image caption generator.",
    long_description="This project was orignally completed as a jupyter notebook assignment for a Deep Learning course at the Technical University of Eindhoven, and is based on the paper [Show and Tell: A Neural Image Caption Generator](https://arxiv.org/abs/1411.4555) by Vinyals et al. in 2015.",
    long_description_content_type="text/markdown",
    install_requires=[
        "numpy==1.19",
        "matplotlib",
        "tensorflow==2.4.3",
        "keras==2.4.3",
        "pandas==1.3.2",
        "ipykernel",
        "nltk==3.6.2",
        "sklearn",
    ],
    tests_require=["pytest"],
    python_requires="==3.8.10",
    author="Eliza Starr",
    author_email="eliza.r.starr@gmail.com",
    license="MIT",
)
