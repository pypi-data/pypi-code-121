from setuptools import find_packages, setup

with open('README.md', 'r') as f:
    readme = f.read()

setup(
    name='mf-python-tools',
    version='0.6',
    description='MF some tools for Python',
    # long_description=readme,
    keywords=['json', 'logging'],
    author='fangsy',
    author_email='fsy7901@163.com',
    url='https://github.com/fangsy/mf-python-tools',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    install_requires=['json-logging-py'],
    include_package_data=True,
    packages=find_packages(),

)
