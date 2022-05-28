from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as file:
    long_description = file.read()

with open("requirements.txt") as file:
    install_requires = file.read().splitlines()

classifiers = [
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Intended Audience :: Science/Research",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "License :: OSI Approved :: MIT License",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Games/Entertainment :: Puzzle Games",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

setup(
    name="gym_simplifiedtetris",
    version="0.4.1",
    author="Oliver Overend",
    author_email="ollyoverend10@gmail.com",
    url="https://github.com/OliverOverend/gym-simplifiedtetris",
    description="Simplified Tetris environments compliant with OpenAI Gym's API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    python_requires=">=3.8, <3.10",
    packages=find_packages(where="gym_simplifiedtetris"),
    install_requires=install_requires,
    classifiers=classifiers,
    package_dir={"": "gym_simplifiedtetris"},
    keywords="tetris, gym, openai-gym, reinforcement-learning, research, reward-shaping",
)
