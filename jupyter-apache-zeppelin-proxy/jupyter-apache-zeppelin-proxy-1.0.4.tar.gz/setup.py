from pathlib import Path

import setuptools

tests_require = [
    "pytest",
    "pytest-cov",
]

HERE = Path(__file__).parent.resolve()
long_description = (HERE / "README.md").read_text()

setuptools.setup(
    name="jupyter-apache-zeppelin-proxy",
    version="1.0.4",
    url="https://github.com/tiaden/jupyter-apache-zeppelin-proxy",
    author="Edem Tiassou",
    author_email="workmail.edem@gmail.com",
    license="MIT LICENSE",
    description="Jupyter Server Proxy for Apache Zeppelin",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["tests"]),
    keywords=[
        "Jupyter",
        "Jupyter Proxy",
        "Jupyter Server Proxy",
        "Apache Zeppelin Integration for Jupyter",
        "Apache Zeppelin",
        "Apache Zeppelin Proxy"
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
    tests_require=tests_require,
    extras_require={"dev": ["black", "ruamel.yaml"] + tests_require},
    entry_points={
        # jupyter-server-proxy uses this entrypoint
        "jupyter_serverproxy_servers": ["zeppelin = jupyter_apache_zeppelin_proxy:setup_apache_zeppelin"],
    },
    package_data={"jupyter_apache_zeppelin_proxy": ["icons/*"]},
)
