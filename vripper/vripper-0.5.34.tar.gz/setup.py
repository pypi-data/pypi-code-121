import setuptools

from generate_supported_host_markdown import get_bullet_points

with open("README.md", "r") as fh:
    long_description = fh.read()

long_description = long_description.replace(" [here](vripper/parser).", ":\n\n" + get_bullet_points())

setuptools.setup(
    name="vripper",
    version="0.5.34",
    author="vka",
    description="A Python implementation of VRipper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=("test",)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["requests", "lxml", "python-resize-image", "gallery-dl", "commmons"]
)
