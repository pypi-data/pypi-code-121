from distutils.core import setup
from setuptools import find_packages

setup(name='typewebio',  # 包名
      version='0.0.1',  # 版本号
      description='Write interactive web app in declaration way.',
      long_description='https://github.com/luxuncang/TypeWebIo',
      author='ShengXin Lu',
      author_email='luxuncang@qq.com',
      url='https://github.com/luxuncang/TypeWebIo',
      install_requires=['pywebio'],
      license='MIT',
      packages=find_packages(),
      include_package_data = True,
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Topic :: Software Development :: Libraries'
      ],
      )