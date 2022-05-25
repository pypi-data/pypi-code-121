from setuptools import setup, find_packages


setup(
    name='kavyanarthaki',
    version='0.2.0',
    license='MIT',
    author="Prof. Achuthsankar S Nair, Vinod M P",
    author_email='sankar.achuth@gmail.com, mpvinod625@gmail.com',
    packages=find_packages('src'),
    include_package_data=True,
    package_data={
        "": ["*.txt"],
        "kavyanarthaki": ["data/*.csv"],
    },
    package_dir={'': 'src'},
    url='https://github.com/dcbfoss/vritham',
    keywords='kavyanarthaki malayalam meter analysis',
    install_requires=[],
)
