from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='SLYLogin',
  version='0.3.2',
  description='',
  long_description='This is a simple login library that will check if a username and password are a match on a line in a accounts file. Format of file must be USERNAME PASSWORD. The library takes three inputs, username, password, accountsFile. Register function takes 3 inputs, username, password, accountFile. Then it stores the username and password in the accountFile by appending it to the existing data. genPassword takes one input which is the length of the generated password and will return the password. View accounts takes the account file and prints the contents if the user is logged in. ViewAccounts takes loggedIn boolean and accounts file input.',
  url='',  
  author='Hayden Cunningham',
  author_email='HaydenCunningham5@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='Login', 
  packages=find_packages(),
  install_requires=[' ']
)