from setuptools import setup
from setuptools import find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='SomeTools',
      version='0.1.38',
      description="Some python tools",
      author="zhangkun",
      author_email="zk.kyle@foxmail.com",
      project_urls={
          'Documentation': 'https://github.com/584807419/SomeTools',
          'Funding': 'https://github.com/584807419/SomeTools',
          'Source': 'https://github.com/584807419/SomeTools',
          'Tracker': 'https://github.com/584807419/SomeTools',
      },
      keywords=("Python", "Tools"),
      license='',
      long_description=long_description,  # 包的详细介绍，一般在README.md文件内
      long_description_content_type="text/markdown",
      url="https://pypi.org/project/SomeTools/",  # 自己项目地址，比如github的项目地址
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.8',  # 对python的最低版本要求
      packages=find_packages(),
      install_requires=[
          "DateTime==4.3",
          "loguru==0.5.3",  # 高效优雅的日志显示
          "opencc-python-reimplemented==0.1.6",  # 繁体简体转换
          "redis==4.0.2",
          "aioredis==2.0.1",
          "pillow==8.4.0",
          "chardet==4.0.0",
          "psutil==5.9.0",
          "aiomysql==0.0.22",
          "pymysql==0.9.3",
          # "orjson",  # 底层使用了rust，Python下最快的json库,比 ujson 快 3 倍，比 json 快 6 倍
      ],
      py_modules=['sometools'],
      include_package_data=True,
      platforms="any",
      scripts=[],
      )


# 上传pypi
# python -m pip install --upgrade twine
# python -m twine upload --repository pypi dist/*

# 打包
# https://blog.csdn.net/yifengchaoran/article/details/113447773
# python -m pip install --upgrade pip
# python -m pip install  --upgrade setuptools wheel
# python setup.py sdist bdist_wheel