import setuptools
import jupyter_projector_proxy
from pathlib import Path

HERE = Path(__file__).parent.resolve()
long_description = (HERE / "README.md").read_text()

setuptools.setup(
    name="jupyter-projector-proxy",
    version="1.0.9",
    url="https://github.com/tiaden/jupyter-projector-proxy",
    author="Edem Tiassou",
    author_email="workmail.edem@gmail.com",
    license="MIT LICENSE",
    description="Jupyter extension to proxy Jetbrains IDEs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["tests"]),
    keywords=[
        "Jupyter",
        "Jupyter Proxy",
        "Jupyter Server Proxy",
        "Jetbrains",
        "IntelliJ",
        "PyCharm",
        "DataGrip",
        "WebStorm",
        "Goland",
        "Clion",
        "PhpStorm",
        "RubyMine",
    ],
    classifiers=[
        "Framework :: Jupyter",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires="~=3.8",
    install_requires=[
        "jupyter-server-proxy"
    ],
    entry_points={
        # jupyter-server-proxy uses this entrypoint
        'jupyter_serverproxy_servers': jupyter_projector_proxy.get_projector_servers()
    },
    package_data={
        'jupyter_projector_proxy': ['icons/*'],
    },
)
