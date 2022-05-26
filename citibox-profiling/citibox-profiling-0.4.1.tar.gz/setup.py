import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="citibox-profiling",
    version="0.4.1",
    author="Citibox",
    description="Citibox profiling tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/citibox/citibox-profiling",
    packages=setuptools.find_namespace_packages(include=["citibox.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=['protobuf~=3.19.0', 'google-cloud-profiler==2.0.4']
)
