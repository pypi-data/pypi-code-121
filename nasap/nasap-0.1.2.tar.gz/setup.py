import sys, os
from setuptools import setup,find_packages

def main():
  root = os.path.abspath(os.path.dirname(__file__))
  try:
    import pyBigWig
  except ImportError:
    os.system('pip install pyBigWig')
    os.system('pip install deeptools')

  with open(os.path.join(root, 'requirements.txt')) as f:
    install_requires = f.read().splitlines()

  if float(sys.version[:3])<=3.6:
    sys.stderr.write("CRITICAL: Python version must be >= 3.6x!\n")
    sys.exit(1)

  setup(
    name='nasap',
    version='0.1.2',
    description='This is a test of the setup',
    author='biodancer',
    author_email='szxszx@foxmail.com',
    url='https://github.com/biodancerwanghzi/nasap/',
    # packages= find_packages(exclude=["back"]),
    packages=['nasap'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    data_files=[('nasap/scripts/', ['nasap/scripts/preprocess.bash', 'nasap/scripts/map1.bash', 'nasap/scripts/map2.bash'])],
    entry_points={
      'console_scripts': [
        'nasap=nasap.nasap:main',
        'batch_nasap=nasap.batch_nasap:main'
      ]
    },
    install_requires=install_requires,
    extras_require={'network': [
      'networkx',
      'community'
    ]},
    zip_safe = True
  )

if __name__ == '__main__':
  main()