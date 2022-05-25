from setuptools import setup, find_packages
from os import path

setup(
    name='esi_maker',
    py_modules=['esi_maker'],
    version='0.15',
    license='LGPLv2.1',
    description='This is a python module to make, load and unzip esi files',
    author='Rainbow-Dreamer',
    author_email='1036889495@qq.com',
    install_requires=['pydub'],
    url='https://github.com/Rainbow-Dreamer/esi_maker',
    download_url=
    'https://github.com/Rainbow-Dreamer/esi_maker/archive/0.15.tar.gz',
    keywords=['esi', 'sound source', 'music'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    include_package_data=True)
