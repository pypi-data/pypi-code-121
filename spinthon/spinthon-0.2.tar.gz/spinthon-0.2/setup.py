from setuptools import setup

setup(name='spinthon',
      version='0.2',
      description='A python package intended to simulate spin dynamics',
      url='http://github.com/bennomeier/spinthon',
      author='Benno Meier',
      author_email='meier.benno@gmail.com',
      license='MIT',
      packages=['spinthon'],
      install_requires = [
          'numpy',
          'scipy',
          'spindata'
          ],
      zip_safe=False)
