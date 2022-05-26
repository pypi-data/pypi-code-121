import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="JPSLUtils",
    version="0.5.9",
    description="Utilities for Jupyter Physical Science Lab project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JupyterPhysSciLab/JPSLUtils",
    author="Jonathan Gutow",
    author_email="gutow@uwosh.edu",
    license="GPL-3.0+",
    packages=setuptools.find_packages(),
    package_data={'JPSLUtils': ['javascript/*.js']},
    include_package_data=True,
    install_requires=[
        'jupyter>=1.0.0',
        'JPSLMenus'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: JavaScript',
        'Operating System :: OS Independent'
    ]
)
