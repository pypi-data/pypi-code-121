'''Setup file for fhirgenerator package'''
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = ["fhir.resources>=6.2.2", "Faker>=13.3.4", "orjson>=3.6.8"]

setuptools.setup(
    name="fhirgenerator",
    version="0.1.4",
    author="Andrew Stevens",
    author_email="andrew.stevens@gtri.gatech.edu",
    description="A package to generate FHIR Resources using a configuration file",
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SmartChartSuite/FHIRGenerator",
    project_urls={
        "Bug Tracker": "https://github.com/SmartChartSuite/FHIRGenerator/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.10",
    package_data={'fhirgenerator.tests.input': ['config.json']},
    entry_points={
        'console_scripts': ['fhirgenerator=fhirgenerator.command_line:main']
    }
)
