import setuptools


with open('README.rst', 'r', encoding='utf-8') as f:
    main_description = f.read()

setuptools.setup(
    name='number-conversions',
    version='0.0.7',
    author='Muremwa',
    author_email='danmburu254@gmail.com',
    url='https://github.com/muremwa/number-conversions',
    description='Convert numbers between different bases.',
    long_description=main_description,
    long_description_content_type='text/x-rst',
    packages=setuptools.find_packages(),
    package_data={'prep': ['*.txt', '*.csv']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
