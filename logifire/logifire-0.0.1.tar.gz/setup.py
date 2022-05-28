import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="logifire",
    version="0.0.1",
    author="Dmitry Parfyonov",
    author_email="parfyonov.dima@gmail.com",
    description="Logs manager with mute log feature at different levels: process, server, cluster",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dparfyonov/logifire",
    project_urls={
        "Bug Tracker": "https://github.com/dparfyonov/logifire/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: System :: Logging"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
