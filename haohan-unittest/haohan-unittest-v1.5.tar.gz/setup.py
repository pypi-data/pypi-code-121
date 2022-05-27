from distutils.core import setup

setup(
    name = 'haohan-unittest',#需要打包的名字
    version = 'v1.5',#版本
    author = 'Javen', # 作者
    packages = ['unittest', 'unittest/test', 'unittest/test/testmock']#需要打包的的目录
)