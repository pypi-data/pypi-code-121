import os
import setuptools


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setuptools.setup(
    name="trops",
    version="0.2.10",
    author="Koji Tanaka",
    author_email="kojiwelly@gmail.com",
    description=("Track operations"),
    long_description_content_type="text/x-rst",
    license="MIT",
    keywords="linux system administration",
    url="http://github.com/kojiwell/trops",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    long_description=read('README.rst'),
    python_requires='>=3.8',
    install_requires=[
        "tabulate >= 0.8.9"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        'console_scripts': ['trops=trops.exec:main'],
    },
)
