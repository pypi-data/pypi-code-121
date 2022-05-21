from unicodedata import name
import setuptools

setuptools.setup(
    name="PowerI2C",
    version="0.0.3",
    author="Cristian Martinez y Alberto Mercado",
    description="Esta libreria se conecta a un arduino mediante protocolo I2C, donde se pueden ingresar comandos para solicitar datos tipo float al arduino",
    packages=["PowerI2C"]
)