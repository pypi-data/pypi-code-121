from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name='pymathics',
    author="Jeroen van Rensen",
    author_email='jmjrensen@jcjcj.nl',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A Simple Arithmetic Package",
    install_requires=[],
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    packages=find_packages(include=['pymathics', 'pymathics.*']),
    test_suite='tests',
    tests_require=['pytest>=3'],
    url='https://github.com/pymathics/pymathics',
    version='0.1.0',
    zip_safe=False,
)
