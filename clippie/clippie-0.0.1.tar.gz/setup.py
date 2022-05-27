import os
from setuptools import setup, find_packages

setup(
    include_package_data=True,
    install_requires=["uvicorn", "fastapi", "pandas","pyspark","openpyxl"],
    zip_safe=False,
    keywords="Retail Data application",
    entry_points={
        "console_scripts": ["clippie=clippie.main:run"]
    },
)
