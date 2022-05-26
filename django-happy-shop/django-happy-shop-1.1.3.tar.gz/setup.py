from setuptools import setup, find_packages

with open("/www/wwwroot/mall.lotdoc.cn/django-happy-shop/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-happy-shop",
    version="1.1.3",
    author="幸福关中",
    author_email="1158920674@qq.com",
    description="一个可快速集成到任何django项目的轻量级商城模块！",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://www.lotdoc.cn/blog/topic/detail/5/",
    project_urls={
        "Bug Tracker": "http://www.lotdoc.cn",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data = True,
    python_requires=">=3.6",
    install_requires = [
        "Django >= 3.2",  # Replace "X.Y" as appropriate
        "Pillow >= 9.0.1",
        "python-alipay-sdk >= 3.0.4",
        "django-cors-headers >= 3.11.0",
        "django-crispy-forms >= 1.14.0",
        "django-filter >= 21.1",
        "coreapi >= 2.3.3",
        "djangorestframework >= 3.13.1",
        "drf-extensions >= 0.7.1"
    ]
)

# setup()