from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name="sanmu",
    version="0.1.1",
    author="dongfangtianyu",
    description="用Excel描述测试用例的UI自动化测试框架，基于Selenium 和 UnitTes",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/dongfangtianyu/sanmu",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={
        "": ["*.html"],
    },
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "sanmu = sanmu.__main__:main",
        ],
    },
    install_requires=[
        "webdriver-manager",
        "selenium",
        "openpyxl",
        "pydantic",
        "ddt",
        "pytest",
        "pytest-html",
    ],
)
