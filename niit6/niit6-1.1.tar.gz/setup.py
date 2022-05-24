from distutils.core import setup
setup(
    name='niit6',#需要发布包的名称
    version='1.1',#版本号
    description='这是我的一个测试包',#包的描述
    author='myx',#作者
    author_email='1522038992@qq.com',
    py_modules=['niit6.class6','niit6.student']#需要发布模块
)

#python setup.py  sdist   #发布
#python setup.py  install  #安装