import setuptools
import subprocess

remote_version = (
    subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
    .stdout.decode("utf-8")
    .strip()
)
assert "." in remote_version

setuptools.setup(
    name="muvinai",
    version=remote_version,
    author="muvinai",
    description="Utilities for muvinai developers",
    long_description="Muvinai Python package",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    package_data={"muvinai": ["VERSION"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['gspread', 'cryptography', 'python-dotenv', 'mercadopago', 'pymongo[srv]', 'iso8601'],
)

