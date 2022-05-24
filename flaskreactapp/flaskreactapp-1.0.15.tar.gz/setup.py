import setuptools

resources_dir = "frontend/build"

requirements_file = 'backend/requirements.txt'

# read requirements from file
with open(requirements_file) as fh:
    requirements = fh.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="flaskreactapp",
    version="v1.0.15".replace('v', ''),
    author="IBM",
    author_email="ilyashn@il.ibm.com",
    description="Flask and react application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ilyashnil/flash-react-app",
    install_requires=requirements,
    packages=setuptools.find_packages(),
    license='Apache License 2.0',
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
    package_data={"": ["LICENSE.txt",
                       requirements_file,
                       f"{resources_dir}/*.css",
                       f"{resources_dir}/*.js",
                       f"{resources_dir}/*.png",
                       f"{resources_dir}/*.svg", ]},
    include_package_data=True
)
