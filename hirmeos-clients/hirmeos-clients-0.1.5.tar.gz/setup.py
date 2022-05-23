from setuptools import setup


with open('README.rst', 'r') as f:
    long_description = f.read()


setup(
    name='hirmeos-clients',
    version='0.1.5',
    author='Rowan Hatherley',
    author_email='rowan.hatherley@ubiquitypress.com',
    description='Python API clients for the HIRMEOS project.',
    install_requires=[
        'requests>=2.0,<3.0',
        'PyJWT>=2.0,<2.2',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/ubiquitypress/hirmeos-clients/',
    packages=['hirmeos_clients'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7'
)
