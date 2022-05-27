import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="agv-fact",
    version="1.0.1.0",
    author="Andres Alvarado Vazquez",
    author_email="andres@agavesoft.com.mx",
    description="Libreria para generar xml y realizar el timbrado",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/fact",
    packages=setuptools.find_packages(),
    package_data={'fact.generator': '*', 'fact.generator.cadenaoriginal_3_3_local': '*'},
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)