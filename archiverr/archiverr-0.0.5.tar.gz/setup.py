import setuptools, os

with open("README.md", "r") as fh:
    long_description = fh.read()

def get_packages(package):
    """Return root package and all sub-packages."""
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]
        
setuptools.setup(
     name='archiverr',  
     version='0.0.5', #0.4.4 test server
     scripts=['archiver'] ,
     author="Théo Hurlimann",
     author_email="author@example.com",
     description="Archiverr is a tool to archive files and folders based on his sha1",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/theohrlmnn/archiver",
     #packages=['src'],
     packages=get_packages("src"),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
    #setup_requires=["numpy"],
    install_requires=[
        #"setuptools>=58",
        "Flask>=2.1.1",
        "numpy>=1.22.3",
        "pandas>=1.4.2",
        "py7zr>=0.17.4",
        "toml>=0.10.0",
        "orjson>=3.6.7",
        "python-magic>=0.4.26",
        "progress>=1.6",
    ],
    python_requires='>=3.10',

 )