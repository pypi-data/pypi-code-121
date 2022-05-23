import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dvadmin-upgrade-center",
    version="1.0.2",
    author="DVAdmin",
    author_email="liqiang@django-vue-admin.com",
    description="适用用 django-vue-admin 的升级中心后端插件",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/huge-dream/dvadmin-upgrade-center",
    packages=setuptools.find_packages(),
    python_requires='>=3.7, <4',
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
