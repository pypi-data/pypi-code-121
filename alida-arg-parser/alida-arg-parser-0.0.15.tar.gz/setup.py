import setuptools

setuptools.setup(
    name="alida-arg-parser",
    version="0.0.15",
    author="Alida research team",
    author_email="salvatore.cipolla@eng.it",
    description="Python argparser modified for Alida services",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires = [
        "jinja2>=2.10"
        ],
)
