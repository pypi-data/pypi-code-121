import setuptools

# 读取项目的readme介绍
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ToolXmind2Testcase",  # 项目名称，保证它的唯一性，不要跟已存在的包名冲突即可
    version="0.0.15",
    author="xu.nie",  # 项目作者
    author_email="xu.nie@shopee.com",
    description="脑图转换为Excel",  # 项目的一句话描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",  # 项目地址
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'ToolXmind2Testcase = ToolXmind2Testcase.convert_xmind_to_excel:convert'
        ]
    },
    install_requires=[
        'xmindparser',
        'pandas',
        'click',
        'xlsxwriter'
    ]
)
