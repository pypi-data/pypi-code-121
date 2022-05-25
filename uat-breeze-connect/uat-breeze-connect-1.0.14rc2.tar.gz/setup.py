import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="uat-breeze-connect",
    version="1.0.14rc2",
    author="UAT Breeze Connect",
    author_email="test@mail.com",
    description="UAT Breeze Connect",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['python-socketio[client]','requests'],
    url="https://github.com/pypa/sampleproject",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
