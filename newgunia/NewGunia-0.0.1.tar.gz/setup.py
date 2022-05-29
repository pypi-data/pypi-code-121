#понадобится модуль
import setuptools

with open("README.MD", "r") as f:
    long_description = f.read()



setuptools.setup(
    name = "NewGunia", #название пакета
    version = "0.0.1", #версия пакета
    autor = "Me",
    autor_email = "nikolia1987cool@gmail.com",
    description = "New Gunia", #краткое описание
    long_description = long_description, #длинное описание берём из long_desc
    long_description_content_type = "text/markdown",
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires = '>=3.6' #требуемая версия
)
