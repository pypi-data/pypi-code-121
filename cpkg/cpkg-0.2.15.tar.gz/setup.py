import setuptools
import os
from platform import system
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name="cpkg",
    version="0.2.15",
    author="xiongtianshuo",
    author_email="Mr_Xiongts@163.com",
    description="A package that creates a package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seoul2k/cPkg",
    project_urls={
        "Bug Tracker": "https://github.com/seoul2k/cPkg/issues",
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Development Status :: 3 - Alpha',
    ],
    packages=['cpkg/'],
    python_requires=">=3",
    options={
        'entry_points': {
            'console_scripts': [
                'createpkg = cpkg.cpkg:main'
            ]
        }
    },
    entry_points={
        'console_scripts': [
            'createpkg = cpkg.cpkg:main'
        ]
    }
)
