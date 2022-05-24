from setuptools import setup, find_packages

classifiers = [
  'License :: OSI Approved :: MIT License',
  'Intended Audience :: Developers',
  'Operating System :: OS Independent',
  'Programming Language :: Python :: 3.5',
  'Programming Language :: Python :: 3.6',
  'Programming Language :: Python :: 3.7',
  'Programming Language :: Python :: 3.8',
  'Programming Language :: Python :: 3.9'
]

setup(
    name='FreeFortniteAPI',
    version='1.0.3',
    description='Easy to use FreeFortniteAPI module.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='',
    author='faktor',
    author_email='minibots010@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='FreeFortniteAPI',
    packages=find_packages(),
    install_requires=['requests']
)