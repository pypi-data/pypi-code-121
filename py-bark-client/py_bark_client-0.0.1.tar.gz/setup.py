from setuptools import setup,find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py_bark_client",
    version="0.0.1",
    author="Rockie Cui",
    author_email="rockiecxh@gmail.com",
    description="Bark client for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url='https://github.com/rockiecxh/py-bark-client',
    project_urls={
        "Bug Tracker": "https://github.com/rockiecxh/py-bark-client/issues",
    },
    install_requires=["requests>=2.25.1"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.5",
)
