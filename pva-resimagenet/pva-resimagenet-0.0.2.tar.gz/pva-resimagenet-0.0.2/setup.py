import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pva-resimagenet",
    version="0.0.2",
    author="Vadim Pashkin",
    author_email="vaplev@mail.ru",
    description="NN based on U-Net and DenseNet for image restoration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tailtoon/ResImageNet",
    project_urls={
        "Bug Tracker": "https://github.com/Tailtoon/ResImageNet/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        'scikit-image',
        'matplotlib',
        'torch',
        'torchvision',
        'torchaudio',
        'torchinfo',
    ],
    python_requires="==3.8.10",
)