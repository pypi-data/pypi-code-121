import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="human_cver",
    version="0.1.0",
    author="Wenkai Liu",
    author_email="wenkai_liu@hust.edu.cn",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wkailiu/human_cver",
    project_urls={
        "Bug Tracker": "https://github.com/wkailiu/human_cver/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.yaml", ],
        # And include any *.msg files found in the 'hello' package, too:
        # "hello": ["*.msg"],
    },
    python_requires=">=3.6",
    install_requires=[
        "rich>=11.0",
        "scipy",
        "opencv-python",
        "logzero",
        "pytorch_lightning",
        "omegaconf",
        "psutil",
    ],
    entry_points={
        'console_scripts': [
            'train=human_cver:train_main',
            'make_config=human_cver:make_config',
        ]
    }
)