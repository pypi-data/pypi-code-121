import setuptools

setuptools.setup(
    author="Aptos Labs",
    author_email="opensource@aptoslabs.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    install_requires=['pynacl', 'requests'],
    name="aptos_sdk",
    python_requires='>=3.7',
    url="https://github.com/aptos-labs/aptos-core",
    version="0.0.1",
)
