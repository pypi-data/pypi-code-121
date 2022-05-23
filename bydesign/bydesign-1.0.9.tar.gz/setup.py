from setuptools import setup, find_packages

setup(
    name="bydesign",
    version="1.0.9",
    author="Velocity Web Works",
    author_email="john@velocitywebworks.com",
    # url=""
    packages=find_packages(),
    install_requires=[
        'django',
    ],
    scripts=[],
    include_package_data=True,
    zip_safe=False,
)
