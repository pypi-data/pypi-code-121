
import setuptools
 
with open("README.txt", "r") as fh:
    long_description = fh.read()
 
setuptools.setup(
    # Here is the module name.
    name="FW4py",
 
    # version of the module
    version="0.0.3",
 
    # Name of Author
    author="Dylan Marsella",
 
    # your Email address
    author_email="dylanmarsella1@gmail.com",

    long_description ='You can click the Home page link or you can click this link: "https://github.com/dmars12345/FW4py" to view doucmentation for this module.',


    long_description_content_type='text/markdown',
 
   
    description="A module made for people who want to use the Publisher FreeWheel API.",
 
 
 
    url="https://github.com/dmars12345/FW4py",
    packages=setuptools.find_packages(),
 
 
    # if module has dependencies i.e. if your package rely on other package at pypi.org
    # then you must add there, in order to download every requirement of package
 
 
 
  install_requires=['pandas','requests','numpy','datetime','dict2xml','xmltodict'],
 
 
    license="MIT",
 
    # classifiers like program is suitable for python3, just leave as it is.
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)