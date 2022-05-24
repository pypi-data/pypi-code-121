import setuptools

#with open("README.md", "r") as fh:
#    long_description = fh.read()

setuptools.setup(
    name='robotics',    # This is the name of your PyPI-package.
    version='1.0.3',
    url='https://github.com/ryanGT/robotics',
    author='Ryan Krauss',
    author_email='ryanwkrauss@gmail.com',
    description="package for robot kinematics analysis",
    #long_description=long_description,
    #long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
