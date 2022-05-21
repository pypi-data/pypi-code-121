import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="slidescore-sdk",
    version="1.2.9",
    author="Slide Score B.V.",
    author_email="info@slidescore.com",
    description="SDK for using the API of Slide Score",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/slide-score/SlideScore-python-sdk",
    packages=setuptools.find_packages(),
	keywords="slidescore,slide score, sdk, api",
	install_requires=[
        'marshmallow>=2,<3',
        'requests',
        'tuspy'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)