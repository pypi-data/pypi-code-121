from setuptools import setup, find_packages

with open("elegant_json/__init__.py", encoding="utf-8") as f:
    line = next(iter(f))
    VERSION = line.strip().split()[-1][1:-1]

with open("README.md") as f:
    readme = f.read()

setup(
    name="elegant-json",
    version=VERSION,
    description="Deal with JSON in an elegant way",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Hanjin Liu",
    author_email="liuhanjin-sc@g.ecc.u-tokyo.ac.jp",
    license="BSD 3-Clause",
    download_url="https://github.com/hanjinliu/elegant-json",
    packages=find_packages(exclude=["docs", "examples", "rst", "tests", "tests.*"]),
    package_data={"elegant_json": ["**/*.pyi", "*.pyi"]},
    install_requires=[],
    python_requires=">=3.8",
)
