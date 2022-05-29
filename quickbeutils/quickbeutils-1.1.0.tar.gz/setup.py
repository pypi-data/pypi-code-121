import setuptools


with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="quickbeutils",
    version="1.1.0",
    author="Eldad Bishari",
    author_email="eldad@1221tlv.org",
    description="All sorts of utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eldad1221/quickbelog",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests>=2.27.1',
        'quickbelog>=1.1.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
