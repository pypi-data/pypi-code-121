import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="devtools-ai",
    version="0.0.2",
    author="Chris Navrides",
    author_email="chris@dev-tools.ai",
    description="A package to bring ai to selenium scripts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dev-tools-ai/python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/dev-tools-ai/python-sdk/issues",
    },
    include_package_data=True,
    packages=setuptools.find_packages(include=["devtools_ai", "devtools_ai.utils"]),
    install_requires=["packaging", "pillow", "requests", "selenium"],
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing :: Unit"
    ],
    python_requires=">=3.7"
)
