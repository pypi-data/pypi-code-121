from setuptools import setup, find_packages


# version = {hyperdata_version}.{mlplatform_version}.{union_test_version}.{human_number}.{test_number}
# ex)        8.4.0             .0                   .0.2.1
# mansu: 0
# jooyoun: 1
# yunho: 2
# IF test completed in feature branch, up union_test_version and upload to pypi
# ex. 8.4.0.0.0.0.1, 2, 3 ... -> test completed -> 8.4.0.0.1.0.0
setup(
    name="mlplatform_lib",
    version="8.4.1.2.14.1.10",
    description="mlplatform_lib",
    author="mlplatform_lib",
    author_email="hdmlplatform@gmail.com",
    url="",
    download_url="",
    install_requires=[
        "pandas>=1.0.1",
        "requests>=2.25.1",
        "dataclasses_json>=0.5.4",
        "inflection>=0.5.1",
        "dataclasses>=0.6",
    ],
    packages=find_packages(exclude=[]),
    keywords=["mlplatform_lib"],
    python_requires=">=3.6",
    package_data={},
    zip_safe=False,
    classifiers=["Programming Language :: Python :: 3.6"],
)
