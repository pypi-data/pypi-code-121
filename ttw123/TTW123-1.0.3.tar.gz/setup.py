import io
import os
from setuptools import setup

scriptFolder = os.path.dirname(os.path.realpath(__file__))
os.chdir(scriptFolder)

# Use the README.md content for the long description:
with io.open("README.md", encoding="utf-8") as fileObj:
    long_description = fileObj.read()

setup(
    name='TTW123',
    version="1.0.3",
    url='https://github.com/gavintan/wfrpc',
    author='Gavin',
    author_email='al@inventwithpython.com',
    description=('你好666'),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='BSD',
    packages=['ttw'],
    install_requires=['psutil>5.9.0'],
    keywords="tt tw ttw",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires=">=3.10"
)
