from setuptools import setup, find_packages
 
setup(name='kea_cerberus',
      version='1.1.7',
      url='http://kea.mx/',
      packages=find_packages(exclude=['tests']),	
      license='MIT',
      author='Cesar Ocotitla',
      author_email='cesar@kea.mx',
      description='Control client, users and service execution of your projects in python',
      zip_safe=False)
