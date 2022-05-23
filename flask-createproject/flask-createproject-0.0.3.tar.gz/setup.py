import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='flask-createproject',
    version='0.0.3',
    author='Mohamed Daif',
    author_email='daif.control@gmail.com',
    description='A utility program to bootstrap flask projects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={"": 'src'},
    packages=setuptools.find_packages('src'),
    python_requires='>=3.9',
    install_requires=['Jinja2>=3.1.2', 'colored>=1.4.3', 'emoji>=1.7.0', 'halo>=0.0.31'],
    package_data={'': ['templates/*.txt']},
    entry_points={
        'console_scripts': [
            'flask-createproject = createproject.main:run',
        ],
    },
)
