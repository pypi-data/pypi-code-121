import codecs

from setuptools import find_packages, setup


def long_description():
    try:
        return codecs.open("README.rst", "r", "utf-8").read()
    except OSError:
        return "Long description error: Missing README.rst file"


setup(
    name="pplay-pygame",
    packages=find_packages(include=["src/pplay-pygame"]),
    version="2.0.1",
    description="A simple game abstraction framework to pygame",
    long_description=long_description(),
    python_requires=">=3.7,",
    author=(
        "Prof. Esteban Clua, "
        "Prof. Anselmo Montenegro, "
        "Gabriel Saldanha, "
        "Adônis Gasiglia, "
        "Yuri Nogueira"
    ),
    author_email=(
        "esteban@ic.uff.br, "
        "anselmo@ic.uff.br, "
        "gabrielcrsaldanha@gmail.com, "
        "adonisgasiglia@id.uff.br, "
        "yurinogueira@id.uff.br"
    ),
    project_urls={
        "Documentation": "https://www2.ic.uff.br/pplay/",
        "Code": "https://github.com/yurinogueira/pplay",
        "Tracker": "https://github.com/yurinogueira/pplay/issues",
    },
    license="GPL-2",
    install_requires=["pygame>=2.1.2"],
    setup_requires=["pytest-runner>=6.0.0"],
    tests_require=["pytest>=7.1.2"],
)
