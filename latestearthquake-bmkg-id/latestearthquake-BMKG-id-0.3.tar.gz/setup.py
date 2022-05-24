"""
https://packaging.python.org/en/latest/tutorials/packaging-projects/
Markdown guide: https://www.markdownguide.org/cheat-sheet/
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="latestearthquake-BMKG-id",
    version="0.3",
    author="Vram Adel Handrio",
    author_email="vram3012@gmail.com",
    description="This package will gate the latest earthquake from BMKG | Meteorological, Climatological,"
                " and Geophysical Agency",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Vram-AH/latest-indonesia-earthquake",
    project_urls={
        "Website": "https://github.com/Vram-AH/latest-indonesia-earthquake",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable"
    ],
    #package_dir={"": "src"},
    #packages=setuptools.find_packages(where="src"),
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
