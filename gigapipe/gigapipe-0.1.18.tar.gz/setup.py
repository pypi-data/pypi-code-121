from setuptools import setup, find_packages

VERSION = "0.1.18"

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Operating System :: Unix',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='gigapipe',
    version=VERSION,
    description='Gigapipe Python Client',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='https://www.gigapipe.com',
    project_urls={
        "Github": "https://github.com/gigapipehq/gigapipe-python-client"
    },
    author='Gigapipe',
    author_email='info@gigapipe.com',
    license='MIT',
    classifiers=classifiers,
    keywords='bigdata, gigapipe, clickhouse',
    packages=find_packages(),
    install_requires=["requests==2.27.1"]
)

#  python3 setup.py sdist bdist_wheel
#  twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
