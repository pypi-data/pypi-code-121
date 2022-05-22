import sys
# from cx_Freeze import setup, Executable
from setuptools import setup, find_packages

build_exe_options = {
    "packages": ["common", "logs", "doc", "server_dir", "unit_tests"],
}
setup(
    name="messenger_server_may",
    version="0.9.1",
    description="server packet",
    packages=find_packages(),
    # options={
    #     "build_exe": build_exe_options
    # },
    author='Egor Varlamov',
    install_requires=['PyQT5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
    # executables=[Executable('server.py',
    #                         # base='Win32GUI',
    #                         targetName='server.exe',
    #                         )]
)
