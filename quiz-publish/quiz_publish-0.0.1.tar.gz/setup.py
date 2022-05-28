import setuptools


setuptools.setup(
    name="quiz_publish",
    version="0.0.1",
    author="Lasha",
    author_email="lasha.alievi.1@btu.edu.ge",
    description="Fibonacci Series",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)