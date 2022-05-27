import setuptools

setuptools.setup(
    name="wet_freight_tce",
    version="1.0.0",
    author="aeorxc",
    description="Calculate TCE (Time Charter equivalents) for wet freight routes",
    url="https://github.com/aeorxc/wet_freight_tce",
    project_urls={
        "Source": "https://github.com/aeorxc/wet_freight_tce",
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pandas", "requests"],
    python_requires=">=3.8",
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
