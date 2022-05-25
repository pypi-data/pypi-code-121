import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="EasyCommandInterface",
    version="1.0.0",
    license='MIT License',
    author="Ashenguard",
    author_email="Ashenguard@agmdev.com",
    description="Basic Console Listener for General Use",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ashenguard/easycommandinterface",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    install_requires=[],
    dependency_links=[]
)
