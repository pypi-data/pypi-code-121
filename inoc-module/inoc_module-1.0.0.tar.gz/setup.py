from setuptools import setup, find_packages

setup(
    name="inoc_module",
    description="Shared code to run the inoc reporter.",
    version="1.0.0",
    author="Rachel Powers",
    author_email="rachelpowers@horizonriver.com",
    install_requires=[
        "beautifulsoup4==4.11.1",
        "mypy==0.950",
        "mysql_connector_repackaged==0.3.1",
        "pandas==1.4.1",
        "python-dotenv==0.20.0",
        "selenium==4.1.5",
        "azure_functions==1.11.2",
    ],
    packages=find_packages(),  # package = any folder with an __init__.py file
)
