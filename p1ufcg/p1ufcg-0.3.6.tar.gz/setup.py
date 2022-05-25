from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='p1ufcg',
      version="0.3.6",
      description='P1 UFCG',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/daltonserey/p1',
      author='Dalton Serey',
      author_email='daltonserey@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      scripts=[],
      python_requires='>=3.6',
      install_requires=[
        'pyyaml>=5.4.1',
        'requests>=2.6.1',
        'cachecontrol[filecache]',
        'tst>=0.17.0',
        'pytest-tst>=0.1.2',
        'questionary',
        'pudb'
      ],
      entry_points = {
        'console_scripts': [
            'p1=p1.commands:main',
        ]
      },
      zip_safe=False)
