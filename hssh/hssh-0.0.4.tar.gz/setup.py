from setuptools import setup

install_requires=['pandas','konlpy','numpy']

setup(
    name='hssh',
    version='0.0.4',
    description='키워드 추출 및 유사도 분석을 위한 hssh 패키지 2702김수진제작',
    url='https://github.com/Sujin-Github/Study2022',
    install_requires=install_requires,
    packages=['hssh']
)
