from setuptools import setup, find_packages


setup(
    name='exergenics',
    version='1.24',
    author="Sanjeevani Avasthi",
    author_email='sanjeevani.avasthi@exergenics.com',
    packages=['exergenics'],
    # package_dir={'': 'src'},
    url='https://github.com/Exergenics/internal-portal-api',
    keywords='exergenics portal api',
    install_requires=[
          'boto3',
          'datetime',
          'requests',
          'urllib3',
          'pandas'
      ],
)
