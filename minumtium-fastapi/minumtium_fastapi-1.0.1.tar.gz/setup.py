import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="minumtium_fastapi",
    version="1.0.1",
    author="Danilo Guimaraes (danodic)",
    author_email="danilo@danodic.dev",
    description="A FastAPI application layer for the minumtium library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/danodic-dev/minumtium-fastapi",
    project_urls={
        "Bug Tracker": "https://github.com/danodic-dev/minumtium-fastapi/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=['pydantic', 'fastapi', 'minumtium', 'minumtium-sqlite', 'minumtium-simple-jwt-auth'],
    python_requires=">=3.6",
)
