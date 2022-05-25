from setuptools import setup, find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()


setup(name="Preciso",
    version="1.0.9",
    author="Michel Perez",
    author_email="michel.perez@insa-lyon.fr",
    description="A package for modelling precipitation in alloys.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://arnall.gitlab.io/preciso/",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    install_requires=['pandas', 
                      'numpy', 
                      'matplotlib', 
                      'jinja2', 
                      'pytest', 
                      'tables', 
                      'h5py', 
                      'jupyter'],
    package_data={'preciso': ['bin/*']})
