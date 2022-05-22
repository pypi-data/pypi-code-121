import sys
# from cx_Freeze import setup, Executable, finder
from setuptools import setup, find_packages

build_exe_options = {
    "packages": ["common", "doc", "log", "server_dir", "unit_tests"],
}
setup(
    name="messenger_client_may",
    version="0.9.1",
    description="client packet",
    packages=find_packages(),
    # options={
    #     "build_exe": build_exe_options
    # },
    author='Egor Varlamov',
    install_requires=['PyQT5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
    # executables=[Executable('client.py',
    #                         # base='Win32GUI',
    #                         targetName='client.exe',
    #                         )]
)
