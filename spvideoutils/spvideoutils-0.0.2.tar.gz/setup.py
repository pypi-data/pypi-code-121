from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="spvideoutils",
    version="0.0.2",
    description="Scripts for saving and splitting video files for other projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha"
    ],
    url="https://github.com/sanjeevs/spvideoutils",
    author="Sanjeev Singh",
    author_email="snjvsingh123@gmail.com",
    entry_points={
        'console_scripts' : [
            'video_capture=spvideoutils.video_capture:main',
            'video_split=spvideoutils.video_split:main',
            'video_merge=spvideoutils.video_merge:main',
            'video_crop=spvideoutils.video_crop:main'
        ]
    },
    install_requires = ['opencv-python'],
    packages = ['spvideoutils'],
    extras_require = {
        "dev": [
            "pytest >= 3.7",
            "check-manifest",
            "twine",
        ],
    }
)