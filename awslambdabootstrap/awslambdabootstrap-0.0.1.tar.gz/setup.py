from setuptools import setup, find_packages

setup(
    name='awslambdabootstrap',
    version="0.0.1",
    license='GPLv3+',
    author="James Davies",
    author_email='james.davies@made.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/malachantrio/aws-lambda-bootstrap',
    keywords='example project',
    install_requires=[
        'boto3',
        'structlog',
        'python-json-logger'
    ]
)
