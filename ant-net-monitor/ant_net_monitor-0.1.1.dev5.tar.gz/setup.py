from setuptools import setup, find_packages

from ant_net_monitor import __version__

setup(
    name="ant_net_monitor",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.2",
        "flask-sqlalchemy>=2.5.1",
        "flask_cors>=3.0.10",
        "click>=8.0.3",
        "psutil>=5.9.0",
        "gunicorn>=20.1.0",
        "pysnmp>=4.4.12",
    ],
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
    url="https://github.com/qzmlgfj/Graduation-Project",
)
