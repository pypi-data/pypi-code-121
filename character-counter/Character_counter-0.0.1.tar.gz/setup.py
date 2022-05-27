import setuptools


setuptools.setup(
    name="Character_counter",
    version="0.0.1",
    author="Viktor Arnautov",
    author_email="arnvikdev@gmail.com",
    description="Count unique charcters in a string or in file",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)