
from setuptools import setup, find_packages

setup(
    name='oblivious_robots_target_searching',
    version='0.0.2',
    license='MIT',
    author="Sairyö No Developers",
    author_email='tech@sairyonodevs.in',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/Sairyo-No-Developers/oblivious-robots-target-search',
    keywords='oblivious robots target searching graph',
    install_requires=[
          'networkx',
          'matplotlib',
          'uuid',
          'names',
          'pytest'
      ],

)