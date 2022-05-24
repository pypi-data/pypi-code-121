import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wks",
    version="0.2.3",
    author="Rhoban team",
    author_email="team@rhoban.com",
    description="Simple dependencies manager for cmake projects in your workspace",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/rhoban/wks/",
    packages=setuptools.find_packages(),
    scripts=["wks"],
    keywords="wks workspace deps",
    install_requires=["colorama", "pyyaml"],
    include_package_data=True,
    python_requires=">=3.6",
)
