import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gotify_message",
    version="0.1.0",
    author="Przemek Bubasr",
    author_email="bubasenator@gmail.com",
    description="Python module to push messages to gotify server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pbubas/gotify_message",
    project_urls={
        "Bug Tracker": "https://github.com/pbubas/gotify_message/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=['requests>=2.25.1'],
)
