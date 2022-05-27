import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="csv_excel_to_mysql",
    version="0.0.1",
    author="KSV Muralidhar",
    author_email="murali_dhar0552@yahoo.com",
    description="Export CSV/Excel to MySQL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        "pandas==1.3.4",
        "numpy==1.21.5",
        "mysql-connector-python==8.0.18",
        "xlrd==2.0.1",
        "openpyxl==3.0.9"
    ],
    python_requires=">=3.7"
)
