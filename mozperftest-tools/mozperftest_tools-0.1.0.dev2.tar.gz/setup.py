import setuptools

PACKAGE_NAME = "mozperftest_tools"
PACKAGE_VERSION = "0.1.0.dev2"

# dependencies
deps = ["numpy >=1.20.2", "matplotlib >=3.4.1,<3.5", "opencv-python", "scipy", "requests"]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/mozperftest-tools",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/mozperftest-tools/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords="mozilla",
    author="Firefox Performance Test Engineering team",
    author_email="perftest@mozilla.com",
    package_dir={"side_by_side": "side_by_side", "utils": "tools/utils"},
    install_requires=deps,
    packages=setuptools.find_packages(where="tools"),
    python_requires=">=3.6,<3.10",
)