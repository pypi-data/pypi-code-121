import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="blp_helpers_data_science", # Replace with your own username
    version="3.0.1",
    author="Leopold Bosankic",
    author_email="leopold.bosankic@outlook.com",
    description="Helpers I use for Data Science projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leugh/helpers_data_science",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)