import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PIHM-utils",
    version="1.0.3",
    author="Yuning Shi",
    author_email="shiyuning@gmail.com",
    packages=["pihm"],
    description="Python scripts to read MM-PIHM input and output files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PSUmodeling/PIHM-utils",
    license='MIT',
    python_requires='>=3.6',
    install_requires=["numpy>=1.19.5"]
)
