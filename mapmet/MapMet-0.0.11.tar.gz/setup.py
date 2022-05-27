from setuptools import setup, find_packages

def parse_requirements():
    with open("requirements.txt", "r") as r:
        lines = r.readlines()
        lines = [l.strip() for l in lines if not "MapMet" in l]
        return lines

VERSION = '0.0.11'
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
    install_reqs = parse_requirements(),
    keywords=['python'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
    ]
)

