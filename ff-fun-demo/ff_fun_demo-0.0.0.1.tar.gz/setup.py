from setuptools import setup

setup(
    name='ff_fun_demo',# 需要打包的名字,即本模块要发布的名字
    version='v0.0.0.1',#版本
    description='special-purpose', # 简要描述
    py_modules=['ff_fun_demo'],   #  需要打包的模块
    author='范范', # 作者名
    author_email='516702882@qq.com',   # 作者邮件
    url='https://gitee.com/fanfan007/py_fun_demo.git', # 项目地址,一般是代码托管的网站
    requires=['datetime','fake_useragent'], # 依赖包,如果没有,可以不要
    license='MIT'
)