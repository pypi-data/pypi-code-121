import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easyfc",
    version="0.0.11",
    author='terryZ',
    author_email="zhengcairui@foxmail.com",
    description="适用于FasS业务的获取参数列表以及返回错误信息库",
    long_description=long_description,  # 包的详细介绍，一般在README.md文件内
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url="https://github.com/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',  # 对python的最低版本要求
)
