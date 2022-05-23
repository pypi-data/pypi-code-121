from setuptools import find_packages, setup

with open(r"..\README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    # 以下为必需参数
    name="hpyculator",
    version="1.4.9",
    description="这是一个基于python的高拓展性计算器",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    long_description=long_description,
    url="https://github.com/HowieHz/hpyculatorPackage",
    author="HowieHz",  # 作者名
    classifiers=[
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=[],
    project_urls={
        "Bug Reports": "https://github.com/HowieHz/hpyculatorPackage/issues",
    },
)
