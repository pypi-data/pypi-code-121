from setuptools import setup, find_packages

VERSION = "0.0.5"
DESCRIPTION= "Execute PowerShell script on remote host"
LONG_DESCRIPTION = "Github page: https://github.com/danielMandelblat/PythonPackages/tree/master/PowerShellRemoteExecuterלו "

#Setting up
setup(
    name='PSRemoter',
    version= VERSION,
    author= 'Daniel Mandelblat',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    include_dirs=[],
    keywords=['powershell', 'remote powershell', 'execute powershell', 'powershell domain', 'domain', 'windows remote', 'windows server'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)
