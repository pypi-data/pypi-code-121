import setuptools



setuptools.setup(
    name="easyi", # Replace with your own username  #自定义封装模块名与文件夹名相同
    version="0.0.1", #版本号，下次修改后再提交的话只需要修改当前的版本号就可以了
    author="王崇林", #作者
    author_email="colins.wang@outlook.com", #邮箱
    description="Use TCP or UDP", #描述
    long_description='Use TCP or UDP', #描述
    long_description_content_type="text/markdown", #markdown
    url="https://github.com/pyconjinji/easyi", #github地址
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", #License
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',  #支持python版本
)
