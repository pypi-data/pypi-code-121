#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: Kerple GL Plugin
# Mail: www.1nick@gmail.com
# Created Time:  2021-12-22 19:17:34
#############################################

from setuptools import setup, find_packages   

with open("README.md") as f:
    long_description = f.read()
    

setup(
    name = "libkdv",
    version = "1.1.18",
    keywords = ["pip", "KDE","heatmap","KDV","KeplerGL"],
    description = "A library of feature heatmap algorithm",
    long_description= long_description,
    long_description_content_type='text/markdown',
    license = "MIT Licence",

    url = "https://github.com/libkdv",  
    author = "Tsz Nam Chan,PakLon Ip, Ryan Leong Hou U",
    author_email = "www.1nick@gmail.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["numpy","pandas"]        
)