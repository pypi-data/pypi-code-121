from setuptools import setup
from io import open


'''
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()
'''

version='0.1.0'

long_description = '''MODULE FOR REAL GHOULS AND DEADINSIDES!!! 1000 - 7???

This module simply performs calculations 
by subtracting 7 from 1000 and beyond, as in the anime "Tokyo Ghoul"

Usage:
    import kaneki \n
    kaneki.torture()

'''

setup(name='kaneki',
      version='0.1.0',
      description='''
        
        MODULE FOR REAL GHOULS AND DEADINSIDES!!! 1000 - 7???
        ==========================
        This module simply performs calculations 
        by subtracting 7 from 1000 and beyond, as in the anime "Tokyo Ghoul" 
      
        ''',

      packages=['kaneki'],
      author='gl0ckchan',
      author_email='dragonelite110@gmail.com',
      long_description=long_description,
      #long_description_content_type='text/x-rst'
      url='https://github.com/gl0ckchan/kaneki',
      zip_safe=False)




