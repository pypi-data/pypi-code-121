from setuptools import setup, find_packages

VERSION = '0.0.10'
DESCRIPTION = 'MapMet Package'
LONG_DESCRIPTION = 'Dummy'

setup(
    name="MapMet",
    version=VERSION,
    author="Taschner-Mandl Group",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["numpy", "opencv-python", "scikit-image", "pandas", "readimc", "natsort"],
    keywords=['python'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
    ]
)