import setuptools
from xiaobaiauto2.__version__ import __version__

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="xiaobaiauto2",
    version=__version__,
    author="Tser",
    author_email="807447312@qq.com",
    description="xiaobaiauto2是对自动化框架的第三次更新，" + \
                "功能覆盖UI自动化与API自动化意在帮助对自动化有更多需求且过多时间写代码的人群，" + \
                "让大家的时间花在业务的实现上",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/xiaobaikeji/xiaobaiauto2",
    packages=setuptools.find_packages(),
    keywords="test auto automation xiaobai xiaobaiauto2 test framework",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "allure-pytest",
        "Appium-Python-Client",
        "jmespath",
        "mitmproxy",
        "pytest",
        "pytest-cov",
        "pytest-sugar",
        "pytest-html",
        "pytest-ordering",
        "pytest-rerunfailures",
        "pytest-xdist",
        "pytest-instafail",
        "pyyaml",
        "requests",
        "selenium",
        "pyperclip"
    ],
    package_data={
        'xiaobaiauto2': [
            'data/favicon.ico',
            'data/xiaobaiauto2.db',
            'test/runTestCase.bat',
            'utils/xiaobaiCaptcha.pyd',
            'utils/adb/adb.exe',
            'utils/adb/AdbWinApi.dll',
            'utils/adb/AdbWinUsbApi.dll'
        ],
    },
    entry_points={'console_scripts': [
        'xiaobaiauto2Timer = xiaobaiauto2.utils.xiaobaiauto2Timer:main',
        'xiaobaiauto2Api = xiaobaiauto2.utils.xiaobaiauto2Tools:cmd',
        'xiaobaiauto2Proxy = xiaobaiauto2.utils.xiaobaiauto2Proxy:cmd',
        'xiaobaiauto2App = xiaobaiauto2.utils.xiaobaiauto2App:adb_cmd',
        'xiaobaiauto2Copy = xiaobaiauto2.utils.xiaobaiauto2Copy:main',
    ]},
)

#python setup.py sdist bdist_wheel

#python -m twine upload dist/*