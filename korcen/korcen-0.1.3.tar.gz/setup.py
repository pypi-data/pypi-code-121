import setuptools

with open("README", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="korcen", # Replace with your own PyPI username(id)
    version="0.1.3",
    author="Tanat",
    author_email="shrbwjd05@naver.com",
    description="한국어 비속어 검열",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TANAT96564/KBWC",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)