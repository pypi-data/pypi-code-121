import pathlib
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setuptools.setup(
      name='MonEater',
      version='0.1.0',
      description='Monitor, transform and upload program output to InfluxDB.',
      long_description=README,
      long_description_content_type="text/markdown",
      url='https://gitlab.cern.ch/berkeleylab/moneater',
      author='Karol Krizka',
      author_email='kkrizka@gmail.com',
      packages=['eaters'],
      modules=['monexec'],
      scripts=['moneater.py','fileeater.py'],    
      install_requires=['influxdb','pyyaml'])
