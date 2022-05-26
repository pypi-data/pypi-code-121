import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='kuploy',  
     version='0.2.0',
     scripts=['kuploy'] ,
     author="Michael Wyraz",
     author_email="kuploy@michael.wyraz.de",
     description="A handy helm3 deployment tool",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/micw/kuploy",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
         "Operating System :: OS Independent",
     ],
 )
