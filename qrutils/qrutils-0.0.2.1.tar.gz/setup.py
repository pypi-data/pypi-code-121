from ensurepip import version
from setuptools import find_packages, setup


def read_requirements(file_name):
    with open(file_name, 'r', encoding='utf8') as f:
        requirements = []
        for line in f:
            requirements.append(line.split('==')[0])
    return requirements
    

setup(
    name="qrutils",
    version="0.0.2.1",
    author='VictorT',
    description = '',
    packages=find_packages(),
        
    # 安装过程中，需要安装的静态文件，如配置文件、service文件、图片等
    data_files=[],

    # 希望被打包的文件
    package_data={},
    # 不打包某些文件
    exclude_package_data={
        '':['__pycache__/*.*']
               },

    # 表明当前模块依赖哪些包，若环境中没有，则会从pypi中下载安装
    install_requires=read_requirements('requirements.txt'),

    classifiers=[
        # 发展时期,常见的如下
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # 开发的目标用户
        'Intended Audience :: Developers',

        # 属于什么类型
        'Topic :: Software Development :: Build Tools',

        # 许可证信息
        'License :: OSI Approved :: MIT License',

        # 目标 Python 版本
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]

)
