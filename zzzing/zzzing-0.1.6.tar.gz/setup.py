from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zzzing",
    version="0.1.6",
    author="xuanzhi33",
    author_email="xuanzhi33@qq.com",
    url="https://zzzing.cn",
    description="zzzing CLI by xuanzhi33",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    license="GPL-3.0",
    install_requires=["requests", "pyquery"],
    packages=find_packages(),
    python_requires=">=3.6",
    console_scripts=["zzzing=zzzing.__main__:main"]
)
