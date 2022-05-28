import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent

README = (HERE / 'README.md').read_text()

setuptools.setup(
    name="polisher",
    version="1.0.2",
    author="Rodrigo da Silva",
    author_email="dasil021@umn.edu",
    description=(
        "polisher is a library that helps you clean your plotly figures.. "
        "This library is inspired by the book Storytelling with Data by Cole "
        "Nussbaumer Knaflic (https://www.kobo.com/us/en/ebook/storytelling-"
        "with-data)."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/rigogsilva/graph-polisher",
    license='MIT',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
