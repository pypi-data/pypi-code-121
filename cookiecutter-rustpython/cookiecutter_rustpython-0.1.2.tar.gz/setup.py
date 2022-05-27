from setuptools import setup
from setuptools_rust import Binding, RustExtension

setup(
    name="cookiecutter_rustpython",
    version="0.1.2",
    rust_extensions=[RustExtension("cookiecutter_rustpython.cookiecutter_rustpython", binding=Binding.PyO3)],
    packages=["cookiecutter_rustpython"],
    # rust extensions are not zip safe, just like C-extensions.
    zip_safe=False,
)