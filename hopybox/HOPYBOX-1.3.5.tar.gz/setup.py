#Copyright owned by HOStudio123 author
#-*- coding:utf-8 -*-
import setuptools
with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()
setuptools.setup(
    name = 'HOPYBOX',
    version = '1.3.5',
    author = 'ChenJinLin',
    author_email = 'hostudio.hopybox@foxmail.com',
    description = 'This is an open source, practical command Python box',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/HOStudio123/HOPYBOX',
    packages = setuptools.find_packages(),
    license = 'GPL-3.0-or-later',
    classifiers = [
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    entry_points={
            "console_scripts":[
                "hopybox=hopybox:pattern",
                ]
            },
    python_requires = '>=3.8',
    install_requires = ['wget','bs4','requests','lxml>=4.6.3','filetype','yagmail','rich>=12.4.1']    
)