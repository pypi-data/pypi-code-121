import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sophon",
    version="0.0.1",
    author="Sophon algorithm team",
    author_email="developer@sophgo.com",
    description="Sophon Artificial Intelligent Library for deep learning on Sophon products.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sophon-ai-algo/sophon-inference",
    project_urls={
        "Bug Tracker": "https://github.com/sophon-ai-algo/sophon-inference/issues",
    },
    classifiers=[
        # 发展时期,常见的如下
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # 开发的目标用户
        'Intended Audience :: Developers',
        # 属于什么类型
        'Topic :: Software Development :: Libraries',
        # 目标 Python 版本
        "Programming Language :: Python :: 3",
        # 许可证信息
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.5",
)