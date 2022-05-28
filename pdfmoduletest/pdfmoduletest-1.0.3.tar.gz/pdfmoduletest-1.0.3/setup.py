# -*- coding: utf-8 -*-

from setuptools import find_packages,setup
setup(
    name='pdfmoduletest',
    version='1.0.3',
    description='https://www.qq.com',
    license='',
    packages=find_packages(exclude=[]),
    url='https://www.qq.com',
    author='作者名',
    author_email='作者@qq.com',
    install_requires=[
        'requests>=2.25.0',
    ],
    package_data={},
    python_requirces='>=3.6',

)

# python setup.py build sdist bdist_wheel
# twine upload dist/*