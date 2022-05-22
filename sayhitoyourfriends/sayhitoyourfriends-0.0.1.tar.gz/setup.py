from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="sayhitoyourfriends",
    version="0.0.1",
    description="DEMO",
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    url="",
    author="Danny2391b",
    author_email="21d.mullins@pcs.hants.sch.uk",
    keywords="core package",
    license="MIT",
    packages=[
        "",
    ],
    install_requires=[
    ],
    extras_require={
        "full": ["click~=8.0.3", "Jinja2~=3.0.2", "rich~=12.2.0", "httpx~=0.22.0"]
    },
    entry_points={
        "console_scripts": [
            "openapidocs=openapidocs.main:main",
            "oad=openapidocs.main:main",
        ]
    },
    include_package_data=True,
    zip_safe=False,
)