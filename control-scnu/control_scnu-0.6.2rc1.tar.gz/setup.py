import setuptools

with open('requirements.txt', encoding="utf-8") as f:
    requirements = f.readlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("description.txt", "r", encoding="utf-8") as fd:
    description = fd.read()


setuptools.setup(
    name="control_scnu",
    # Replace with your own username
    version="0.6.2rc1",
    author="HuaGuangEdu",
    author_email="huaguangcase@163.com",
    description=description,
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7, <3.9',
    include_package_data=True,
)
