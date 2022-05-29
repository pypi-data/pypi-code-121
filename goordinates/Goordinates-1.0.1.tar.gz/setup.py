import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Goordinates",
    version="1.0.1",
    author="Duoslow",
    author_email="heniugur@gmail.com",
    description="Outputs latitude/longitude coordinates from any Google Map URL.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Duoslow/Goordinates",
    project_urls={
        "Bug Tracker": "https://github.com/Duoslow/Goordinates/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=['urllib3','requests']
)