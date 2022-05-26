import setuptools 

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()
   
setuptools.setup(
    name="kinqimen",
    version="0.0.6.3",
    author="Ken Tang",
    author_email="kinyeah@gmail.com",
    install_requires=[            
      ],
	description="Qimendunjia (奇門遁甲) is one of the three greatest Chinese Divination systems ever. This package includes hour-based Qimen and Golden Letter Jade Mirror (金函玉鏡) day-based Qimen",
	long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kentang2017/kinqimen",
	packages=setuptools.find_packages(),
	package_data = {},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)