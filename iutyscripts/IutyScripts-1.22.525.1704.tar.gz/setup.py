from setuptools import setup,find_packages

name="IutyScripts"
version = '1.22.0525.1704'

author = "Iuty"
author_email = "dfdfggg@126.com"

packages = [
        "IutyScripts.coding",
        "IutyScripts.file",
        "IutyScripts.entry",
        "IutyScripts.image",
    ]


#data_files = [(r"D:/templates/","IutyScripts/templates/"),]
#package_dir = {'templates': "IutyScripts/templates"}
scripts = []
install_requires = ["IutyLib"]

entry_points={
        'console_scripts': [
            'ipb = IutyScripts.entry.ipb:main',
            'ifs = IutyScripts.entry.ifs:main',
            'iat = IutyScripts.entry.iat:main',
            
            'imgex = IutyScripts.entry.imgex:main',
            'imgdiv = IutyScripts.entry.imgdiv:main',
            'imgpre = IutyScripts.entry.imgpre:main'
        ]
    }





setup(
    name=name,
    version= version,
    author = author,
    author_email = author_email,
    #data_files = data_files,
    packages=packages,
    #package_dir=package_dir,
    entry_points=entry_points,
    install_requires = install_requires
)