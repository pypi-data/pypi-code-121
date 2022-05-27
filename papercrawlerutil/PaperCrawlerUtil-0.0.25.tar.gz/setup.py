import setuptools  # 导入setuptools打包工具
import PaperCrawlerUtil
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PaperCrawlerUtil",  # 用自己的名替换其中的YOUR_USERNAME_
    version="0.0.25",  # 包版本号，便于维护版本
    author="liwudi.fun",  # 作者，可以写自己的姓名
    author_email="liwudi@liwudi.fun",  # 作者联系方式，可写自己的邮箱地址
    description="a collection of utils used to create crawler and document process",  # 包的简述
    long_description=long_description,  # 包的详细介绍，一般在README.md文件内
    long_description_content_type="text/markdown",
    url="https://github.com/Liwu-di/PaperCrawlerUtil",  # 自己项目地址，比如github的项目地址
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['beautifulsoup4>=4.10.0', 'urllib3>=1.26.8',
                      'requests>=2.27.1', 'fake-useragent>=0.1.11',
                      'pdfplumber>=0.6.2', 'pdf2docx>=0.5.3',
                      'python-docx>=0.8.11', 'googletrans>=4.0.0rc1'],
    python_requires='>=3.6',  # 对python的最低版本要求
)