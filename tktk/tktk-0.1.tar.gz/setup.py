from setuptools import setup,find_packages
setup(name='tktk',
      version='0.1',
      description='tkinter的增强控件,将tkinter的基础控件进行封装,给予更强大的控件功能,所有控件继承于LabelFrame进行封装,使用方法和普通控件没什么区别;',
      classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
      url='https://www.python.org/',
      author='bili:凿寂',
      author_email='mdzzdyxc@163.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=True
     )