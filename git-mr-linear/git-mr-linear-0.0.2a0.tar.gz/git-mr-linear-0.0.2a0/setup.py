import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="git-mr-linear",
    version="0.0.2a",
    author="Donghyeon Kim",
    author_email="dhygns@gmail.com",
    description="A command line utility to list and merge gitlab merge requests while maintaining linear history",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/dhpersonal/git-mr-linear",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)