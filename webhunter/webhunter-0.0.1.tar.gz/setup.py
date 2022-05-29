import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="webhunter",
    version="0.0.1",
    author="xuzhiyu",
    author_email="GloryOfAll1994@gmail.com",
    description="webhunter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xuzhiyu1995/webhunter",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
