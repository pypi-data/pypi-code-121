import shutil

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

try:
    shutil.rmtree('./build')
    shutil.rmtree('./dist')
except OSError as e:
    print("Error: %s - %s." % (e.filename, e.strerror))

setuptools.setup(
    name="TradeGate-Beta",  # This is the name of the package
    version="0.2.1Beta18",
    author="Rustin Soraki",  # Full name of the author
    description="A Trading Gateway",
    long_description=long_description,  # Long description read from the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(where='TradeGates'),  # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],  # Information to filter the project on PyPi website
    python_requires='>=3.6',  # Minimum version requirement of the package
    py_modules=["TradeGate"],  # Name of the python package
    package_dir={'': 'TradeGates'},  # Directory of the source code of the package
    install_requires=['binance-connector', 'requests', 'apscheduler', 'websocket-client', 'urllib3', 'tzlocal<3.0',
                      'pandas', 'pybit']  # Install other dependencies if any
)

# python setup.py sdist bdist_wheel  
# twine check dist/*   
# twine upload dist/*
