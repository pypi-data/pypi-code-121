from setuptools import setup


with open('README.md','r') as f:
    long_description = f.read()


setup(
    name = "blurit",
    version = "0.0.13",
    description = "This package is aimed to build to blur different portions of a image. Currently it blurs eyes in human photograph.",
    py_modules = ["blurit"],
    package_dir = {'':'src'},
    classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Operating System :: OS Independent'
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "opencv-python~=4.1.2",
        "numpy~=1.21",
        "dlib~=19.19.0"
    ],
    extras_require={
        "dev":[
            "pytest>=3.7"
        ],
    },
    url="https://github.com/iampabba/blur-it",
    author="Anubharth Pabba",
    author_email="bharath.pabba1@gmail.com"
)
