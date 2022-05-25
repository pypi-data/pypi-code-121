import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zzd",
    version="0.2.0",
    author="zzd lab", 
	author_email="1965770446@qq.com",
    description="encode and scores", 
	long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/miderxi/zzd",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

