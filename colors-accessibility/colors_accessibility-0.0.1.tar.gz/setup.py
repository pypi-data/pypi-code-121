import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="colors_accessibility",
    version="0.0.1",
    author="Piotr Hryniewicz",
    author_email="phryniewicz.dev@gmail.com",
    description="Package to process and change colors between color spaces and to tweak input colors to meet WCAG 2.1 "
                "accessibility standards.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/phryniewicz/colors-accessibility",
    project_urls={
        "Bug Tracker": "https://github.com/phryniewicz/colors-accessibility/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
