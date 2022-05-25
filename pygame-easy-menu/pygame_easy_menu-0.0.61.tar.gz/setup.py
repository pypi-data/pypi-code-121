import setuptools

with open("README.md", "r") as fh:
    [fh.readline() for i in range(4)]  # remove first 3 line
    long_description = fh.read()

setuptools.setup(
    name="pygame_easy_menu",

    version="0.0.61",

    author="Paul Mairesse",
    author_email="paul.mairesse@free.fr",

    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=setuptools.find_packages(),

    requires=["textwrap3", "pygame", "pathlib", "logging"],

    license="MIT",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
