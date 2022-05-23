from setuptools import setup
from flutter_gen import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="flutter_gen",
    version=__version__,
    author="Pham Xuan Tien",
    author_email="tienpx.x.x@gmail.com",
    description="A code generator for Flutter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tien-px/pt_flutter_tools",
    license="MIT",
    packages=[
        "flutter_gen",
        "flutter_gen/config",
        "flutter_gen/core",
        "flutter_gen/create",
        "flutter_gen/figma",
        "flutter_gen/generate",
        "flutter_gen/intellji",
        "flutter_gen/rename",
        "flutter_gen/template",
        "flutter_gen/utils",
        "flutter_gen_templates",
    ],
    entry_points={"console_scripts": [
        "flutter_gen = flutter_gen.__main__:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3",
    install_requires=[
        "clipboard>=0.0.4",
        "PyYAML>=6.0.0",
        "cssutils>=2.2.0",
        "Jinja2>=2.10",
        "watchdog>=2.1.7",
        "arghandler>=1.2",
        "tqdm>=4.64.0",
        "requests>=2.27.1",
    ],
    include_package_data=True,
)
