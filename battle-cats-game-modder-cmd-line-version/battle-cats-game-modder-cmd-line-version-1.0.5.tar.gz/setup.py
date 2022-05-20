import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(r"I:\coding\python\BCGM-python-cmd-line-version\src\BCGM_PY_CMD\files\version.txt", "r", encoding="utf-8") as fh:
    version = fh.read()

setuptools.setup(
    name="battle-cats-game-modder-cmd-line-version",
    version=version,
    author="jo912345",
    description="A battle cats tool for modifying, encrypting, and decrypting game files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/j0912345/BCGM-Python-cmd-line-version",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"" : "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "colored", "tk", "alive-progress", "pycryptodomex", "requests"
    ],
    include_package_data=True
)
