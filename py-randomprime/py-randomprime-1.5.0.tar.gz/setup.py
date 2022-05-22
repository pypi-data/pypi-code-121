from setuptools import setup
from setuptools_rust import Binding, RustExtension

setup(
    rust_extensions=[
        RustExtension(
            "py_randomprime.rust",
            binding=Binding.PyO3,
            py_limited_api=True,
        )
    ],
)
