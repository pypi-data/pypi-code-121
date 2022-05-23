import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gcp-alpa", # Replace with your own username
    version="0.0.9",
    author="Albert Pang",
    author_email="alpaaccount@mac.com",
    description="GCP API Wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alpaalpa/gcp",
    # packages=setuptools.find_packages(),
    packages=["gcp", "gcp.geocoding"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "munch",
        "requests"
    ]
)
