from setuptools import setup,find_packages
setup(
    name="gjy",
    version="0.3",
    author="gjy",
    description="郭洁迎",
    packages=find_packages('gjy'),
    package_dir={"":"gjy"},
    package_data={
        "":[".txt",".info","*.properties"],
        "":["data/*.*"],
    },
exclude =["*.test","*.test.*","test"]

)
