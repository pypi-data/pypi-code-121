import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="podcast_recommendation",
    version="0.1.8",
    author="Manuel Martinez",
    author_email="manuelalejandromartinezf@gmail.com",
    description="Podcast recommendation algorithm in Neo4j",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ManuelAlejandroMartinezFlores/PodcastRecommendation",
    project_urls={
        "Bug Tracker": "https://github.com/ManuelAlejandroMartinezFlores/PodcastRecommendation/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    package_data={
        '': ['data/*.csv']
    },
    install_requires = ["pandas", "scikit-learn", "neo4j", "numpy"],
    include_package_data = True,
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)