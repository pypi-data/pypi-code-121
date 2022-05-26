import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="quizzii1",
    version="0.0.1",
    author="aaaa1",
    author_email="nodari.guliashvili.2@btu.edu.ge",
    description="quizz",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages= ["quizzi1"], #setuptools.find_packages(where="quizzi1"),
    python_requires=">=3.6",
)
