import setuptools
import seismod1d

long_description = """
Create synthetic seismic
"""

setuptools.setup(
    name="seismod1d",
    version=seismod1d.__version__,
    author="Equinor ASA",
    author_email="eidi@equinor.com",
    description=long_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/equinor/seismod1d",
    packages=setuptools.find_packages(),
    package_data={"seismod1d": ["colormaps/*.dat"]},
    include_package_data=True,
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
        "lasio",
        "segyio",
        "bruges",
        "scikit-learn",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
