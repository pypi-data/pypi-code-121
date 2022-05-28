from setuptools import setup

setup(name='CostaOS',
      version='0.0.2',
      description='为Costa操作系统量身定制的开发库',
      author='远迅科技',
      author_email='yuanxunkj@qq.com',
      url='https://lee.szxinlianyun.com',
      packages=['Costa'],
      install_requires=['pywin32==304', 'tkinterweb==3.13.2'],
      python_requires='>=3'
  )