from setuptools import find_packages, setup

setup(name='tensorscout',
      version='1.0.1',
      description='Parallel processing for tensors. A Python library.',
      url='https://github.com/andrewrgarcia/tensorscout',
      author='Andrew Garcia, PhD',
      license='MIT',
      packages=find_packages(include=['tensorscout']),
      zip_safe=False)
