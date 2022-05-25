import setuptools
# with open("README.md", type,encoding='UTF-8') as f:
with open("README.md", "r",encoding='UTF-8') as fh:
    long_description = fh.read()
setuptools.setup(
    name="formatData",  # 模块名称
    version="1.0",  # 当前版本
    author="panxiuqiang",  # 作者
    author_email="501274367@qq.com",  # 作者邮箱
    description="这是一个关于python web 后端json数据返回的工具",  # 模块简介
    long_description=long_description,  # 模块详细介绍
    long_description_content_type="text/markdown",  # 模块详细介绍格式
    url="https://github.com/strongxiuxiu/formatData.git",  # 模块github地址
    packages=setuptools.find_packages(),  # 自动找到项目中导入的模块
    # 模块相关的元数据
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # 依赖模块
    install_requires=[
    ],
    python_requires='>=3',
)