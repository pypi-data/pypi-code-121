import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="smilewebp",
    version="1.0.0",
    author="Sitthykun LY",
    author_email="ly.sitthykun@gmail.com",
    description="Webp image library for python3.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sitthykun/smilewebp",
    project_urls={
        "Bug Tracker": "https://github.com/sitthykun/smilewebp/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
