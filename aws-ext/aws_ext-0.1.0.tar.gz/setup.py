import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aws_ext",
    version="0.1.0",
    author="Matteo Redaelli",
    author_email="matteo.redaelli@gmail.com",
    description="aws_ext is a set of high level useful functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matteoredaelli/aws_ext",
    project_urls={
        "Bug Tracker": "https://github.com/matteoredaelli/aws_ext/issues",
    },
    license="GPL",
    entry_points={
        "console_scripts": ["aws_ext=aws_ext.command_line:main"],
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
