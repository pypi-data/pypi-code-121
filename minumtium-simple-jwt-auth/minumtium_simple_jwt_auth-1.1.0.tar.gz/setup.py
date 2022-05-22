import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="minumtium_simple_jwt_auth",
    version="1.1.0",
    author="Danilo Guimaraes (danodic)",
    author_email="danilo@danodic.dev",
    description="A JWT token adapter for the minumtium library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/danodic-dev/minumtium-simple-jwt-auth",
    project_urls={
        "Bug Tracker": "https://github.com/danodic-dev/minumtium-simple-jwt-auth/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    packages=['minumtium_simple_jwt_auth'],
    install_requires=['bcrypt', 'pyjwt', 'minumtium'],
    python_requires=">=3.6",
)
