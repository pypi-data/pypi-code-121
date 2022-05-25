import setuptools
import sys

if sys.version_info[0] > 2:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    with open("README.md", "r") as fh:
        long_description = fh.read()

setuptools.setup(
    name="DynamiKontrol-Toolkit",
    version="0.4.5",
    author="The Matrix",
    author_email="contact@m47rix.com",
    description="DynamiKontrol Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/TheMatrixGroup/DynamiKontrol',
    license='MIT',
    install_requires=[
        'opencv-python>=4.4',
        'mediapipe>=0.8.9.1',
        'numpy>=1.22.3',
        'DynamiKontrol',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Hardware",
        "Topic :: System :: Hardware :: Hardware Drivers"
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.4.2",
)
