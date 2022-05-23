import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ecalic",
    version="1.0.1",
    author="Fabrice Couderc",
    author_email="fabrice.couderc@cern.ch",
    description="A package to handle CMS Ecal InterCalibration constants and Ecal geometry",
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.cern.ch/cms-ecal-dpg/ecalic",
    packages=setuptools.find_packages(),
    install_requires=['matplotlib','pandas','lxml','numpy'],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
