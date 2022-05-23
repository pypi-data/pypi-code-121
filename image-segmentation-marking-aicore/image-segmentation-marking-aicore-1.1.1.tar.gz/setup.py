import setuptools

setuptools.setup(
    name="image-segmentation-marking-aicore",
    version="1.1.1",
    author="Ivan Ying",
    author_email="ivan@theaicore.com",
    description="An automated marking system for the image segmentation scenario",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=['requests']
)