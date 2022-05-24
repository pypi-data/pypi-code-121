import setuptools

setuptools.setup(
    name="abc_live_lib",                     # This is the name of the package
    version="1.0.1",                        # The initial release version
    author="Areen Rath",                     # Full name of the author # Long description read from the the readme file
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["abc_live_lib"],             # Name of the python package
    package_dir={'':'.'},     # Directory of the source code of the package
    install_requires=[]                     # Install other dependencies if any
)