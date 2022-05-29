import setuptools

setuptools.setup(
    name="streamlit-searchbox",
    version="0.0.1",
    author="Martin Wurzer",
    author_email="",
    description="Autocomplete Searchbox",
    long_description="A Searchbox that dynamically updates and provides a list of suggestions based on the text input",
    long_description_content_type="text/plain",
    url="",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.6",
    install_requires=[
        "streamlit >= 0.63",
    ],
    extras_require={
        "tests": ["wikipedia"],
    },
)
