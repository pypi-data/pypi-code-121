import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='thepotato',  
     version='1.0.0',
     scripts=['thepotato.py'] ,
     author="Daniel Gomes",
     author_email="danielcerqueira2346@gmail.com",
     description="Esta Biblioteca é e será usada para achar preços reais de commodities",
     long_description_content_type="text/markdown",
     long_description=long_description,
     url="https://github.com/dcgo15/Potato-the-project/",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
