from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='zwsp_char_function',
    version='1.0',
    description='a library that returns a sequence of zero with characters',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Churning Lava',
    author_email='snoopydankl@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='zero width character',
    packages=['zero_width_char'],
    install_requires=['']
)