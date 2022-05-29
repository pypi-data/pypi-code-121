import setuptools

def readme_file():
    with open('README.rst') as rf:
        return rf.read()



setuptools.setup(
    name = 'pyhrms',
    version = '0.3.9',
    author = 'Wang Rui',
    author_email = 'wtrt7009@gmail.com',
    url = 'https://github.com/WangRui5/PyHRMS.git',
    description = 'A powerful GC/LC-HRMS data analysis tool',
    long_description = readme_file(),
    packages = setuptools.find_packages(),
    install_requires = ['numpy>=1.19.2','pandas>=1.3.3'
        ,'matplotlib>=3.3.2','pymzml>=2.4.7','scipy>=1.6.2'
        ,'molmass>=2021.6.18','tqdm >= 4.62.3'],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',

)
