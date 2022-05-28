from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='BMI_APP',
        version='0.1',
        description='BMI, BMI Category, Health Risk calculation',
        long_description=long_description,
        long_description_content_type="text/markdown",
        url='https://github.com/manishgupta-ind/code-20220528-manishgupta',
        author='Manish Gupta',
        author_email='mgupta.power@gmail.com',
        license='MIT',
        python_requires='>=3.6',
        packages=['BMI_APP'],
        install_requires=['BMI_APP'],
        zip_safe=False)
