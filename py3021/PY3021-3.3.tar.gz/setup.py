from setuptools import find_packages,setup
setup(
    name = 'PY3021',#模块名
    version = '3.3', #版本
    packages = find_packages(exclude=[]), #目录所有文件
    url='https://xxx.com', #文件文档下载地址
    author='PY3021', #作者名
    author_email='111@qq.com', #邮箱
    install_requires=['requests>=2.25.0',
                      'lxml',
                      ],
    python_requires=">=3.6",

)

# python setup.py build sdist bdist_wheel  #这个是打包到dist文件夹
# twine upload dist/*  #这个是上传dist到pypi.org