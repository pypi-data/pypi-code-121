import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pygdg",
    version="0.1.2",
    author="GroWaK",
    author_email="me@growak.org",
    description="A simple comand line tool to create game events data for analytics and machine learning use cases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='game machine learning analytics dataset generator',
    url="https://github.com/growak/pygdg",
    project_urls={
        "Roadmap": "https://github.com/growak/pygdg/projects",
        "Bug Tracker": "https://github.com/growak/pygdg/issues"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'click',
        'numpy',
        'pandas',
        'matplotlib'
    ],
    entry_points='''
        [console_scripts]
        pygdg=pygdg.main:main
    ''',
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)