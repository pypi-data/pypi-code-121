import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="current-path",
    version="0.0.1",
    author="jon-edward",
    author_email="arithmatlic@gmail.com",
    description="A small library for getting current path data "
                "for a script that imports this library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jon-edward/current_path",
    package_dir={"current_path": "."},
    py_modules=["current_path.py"],
    python_requires=">=3.6",
)
