from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="umapy",
    version="1.0.0",
    description="A python wrapper for UMA API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rexians",
    author_email="admin@rexiansteam.tk",
    license="MIT",
    url="https://github.com/Rexians/umapy",
    project_urls={
        "Bug Tracker": "https://github.com/Rexians/umapy/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="uma, mcoc, umapy, api, wrapper",
    install_requires=["requests"],
    include_package_data=True,
    python_requires=">=3.6",
)
