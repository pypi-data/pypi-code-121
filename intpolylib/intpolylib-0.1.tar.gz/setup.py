from setuptools import setup, find_packages


setup(
    name='intpolylib',
    version='0.1',
    author="Dariusz Libecki",
    author_email='dariuszlibecki@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/Kerad20/polylib',
    keywords='polynomials',
    install_requires=[
          'numpy',
      ],

)