from setuptools import setup, find_packages

setup(
    name='keap-auth-python',
    version='0.2',
    description='Python SDK for Keap API',
    url='https://bitbucket.org/theapiguys/keap-python',
    author='Brandon@TheAPIGuys',
    author_email='brandon@theapiguys.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'keap = keap.scripts.cli:cli',
        ],
    },
)
