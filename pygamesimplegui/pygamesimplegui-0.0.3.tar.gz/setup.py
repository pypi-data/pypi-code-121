from setuptools import setup, find_packages


setup(
    name='pygamesimplegui',
    version='0.0.3',
    license='MIT',
    author="Praneeth Jain",
    author_email='praneethjain005@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/PraneethJain/PyGame-GUI',
    keywords='pygame simple gui',
    install_requires=[
          'pygame',
      ],

)