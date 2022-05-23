import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="EmojiCloud",
    version="0.1.1",
    author="Yunhe Feng",
    author_email="yunhefengit@gmail.com",
    description="EmojiCloud: a Tool for Emoji Cloud Visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YunheFeng/EmojiCloud",
    project_urls={
        "Bug Tracker": "https://github.com/YunheFeng/EmojiCloud/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    include_package_data=True,
    package_data={
        "EmojiCloud": ["data/Appl/*.png", "data/FB/*.png", "data/Goog/*.png", "data/Joy/*.png", "data/Sams/*.png", "data/Twtr/*.png", "data/Wind/*.png"],
    }
)


