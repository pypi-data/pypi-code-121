from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='checkgstnum',
    version='0.0.1',
    description='to validate gst num',
    long_description='this library helps you to check gst num',
    url='',
    author='bhavdip',
    author_email='bvmbvm48@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='gstvalidatation checking',
    packages=find_packages(),
    install_requires=['']
)
