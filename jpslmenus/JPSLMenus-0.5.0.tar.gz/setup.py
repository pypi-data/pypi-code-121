import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="JPSLMenus",
    version="0.5.0",
    description="Tools to build menus",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JupyterPhysSciLab/JPSLMenus",
    author="Jonathan Gutow",
    author_email="gutow@uwosh.edu",
    license="GPL-3.0+",
    packages=setuptools.find_packages(),
    package_data={'JPSLMenus': ['js/*.js']},
    include_package_data=True,
    install_requires=[
        'jupyter>=1.0.0',
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
