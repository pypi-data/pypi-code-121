from setuptools import setup, find_packages


from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name="justshowit",
    version='0.1',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Jako-K",
    description='Display images without any shenanigans',
    packages=find_packages(),
    install_requires=["opencv_python_headless", "requests", "numpy", "rectpack", "Pillow"],
    keywords=["python", "image", "images", "show", "display"]
)


