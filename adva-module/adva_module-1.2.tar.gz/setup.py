import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

INSTALL_REQUIRES = ['requests',
                    'urllib3',
                    ]

setuptools.setup(
    name="adva_module",
    version="1.2",
    author="Jorge Riveros",
    author_email="christian.riveros@outlook.com",
    license='MIT',
    description='A Python package to get REST API ADVA Information',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cocuni80/adva_module",
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.x',
)
