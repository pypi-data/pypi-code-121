from setuptools import setup, find_packages

with open('README.md', 'r') as file:
    readme = file.read()

with open('VERSION', 'r') as file:
    version = file.readline().rstrip('\n')

setup(
    name='searpent-classy-sdk',
    version=version,
    author='Searpent s.r.o.',
    author_email='support@searpent.com',
    description='SDK for Searpent Classy API',
    long_description_content_type='text/markdown',
    long_description=readme,
    url='https://github.com/searpent/classy-sdk-python',
    license='MIT License',
    project_urls={
        'API documentation': 'https://searpentclassy.docs.apiary.io',
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=[
        'requests',
    ],
    python_requires='>=3.6, <4',
)
