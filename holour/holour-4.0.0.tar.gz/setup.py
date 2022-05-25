import setuptools

with open("README.md", 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="holour",
    version="4.0.0",
    author="Rasmus Lunding",
    author_email="rlh@cs.au.dk",
    description="Collection of common data types",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    url="https://gitlab.au.dk/hrc/common/holour",
    install_requires=[
        'paho-mqtt>=1.6.1',
        'PyYAML>=6.0',
    ],
)
