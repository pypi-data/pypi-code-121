import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Auto-ML-study", # Replace with your own username
    version="0.0.1",
    author="EunJae Yong (Jay Yong)",
    author_email="jayyong.dev@gmail.com",
    description="This library was created for students studying autoML.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dev-jay-yong/Auto-DL-Study",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)