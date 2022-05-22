from setuptools import setup, find_packages

setup(name='naver_translation', # 패키지 명

version='1.0.0',

description='네이버 번역 API를 사용한 비공식 SDK입니다.',

author='VoidAsMad',

author_email='voidasmad@gmail.com',

url='https://discord.gg/B98msXGRB7',

license='MIT', # MIT에서 정한 표준 라이센스 따른다

py_modules=['main'], # 패키지에 포함되는 모듈

python_requires='>=3',

install_requires=[], # 패키지 사용을 위해 필요한 추가 설치 패키지

packages=['naver_translation'] # 패키지가 들어있는 폴더들

)