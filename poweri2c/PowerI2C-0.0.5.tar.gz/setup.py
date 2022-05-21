from setuptools import setup

readme = open("./README.md","r")

setup(
    name="PowerI2C",
    version="0.0.5",
    author="Cristian Martinez y Alberto Mercado",
    description="Esta libreria se conecta a un arduino mediante protocolo I2C, donde se pueden ingresar comandos para solicitar datos tipo float al arduino",
    long_description=readme.read(),
    long_description_content_type="text/markdown",
    packages=["PowerI2C"]
)