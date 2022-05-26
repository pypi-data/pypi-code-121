from setuptools import setup

setup(name='blurp',
      version='0.4',
      description='simples example in the python world',
      url='https://github.com/gdamjan/hello-world-python-package',
      author='x@x.com',
      author_email='x@x.com',
      license='MIT',
      packages=['cool_lib'],
      zip_safe=False,
      entry_points = {
          'console_scripts': ['cool-cmd=cool_lib.__main__:main'],
      }
)
