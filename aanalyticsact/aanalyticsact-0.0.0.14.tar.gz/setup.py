import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aanalyticsact",
    version="0.0.0.14",
    author="Sunkyeong Lee",
    author_email="sunkyeong.lee@concentrix.com",
    description="adobe analytics library for Team ACT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SunkyeongLee/aanalyticsact",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)