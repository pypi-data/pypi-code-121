import setuptools

with open("README.md", "r") as fh:
        long_description = fh.read()
        setuptools.setup(
        name="mapna-mind-sdk",
        version="0.4.2",
        author="Soheil Mehralian, Homa Hasannezhad, Afsaneh Sadeghnezhad",
        author_email="mehralian1@gmail.com",
        description="Mapna MIND Software Development Kit",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://www.mapnaec.com",
        packages=setuptools.find_packages(),
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
        python_requires='>=3',
        )
