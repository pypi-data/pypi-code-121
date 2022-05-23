from distutils.core import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='aioinflux3',
      version='0.0.5',
      description='influxdb python client working with asyncio',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Alexander.Li',
      author_email='superpowerlee@gmail.com',
      url='https://github.com/ipconfiger/aio-influx',
      install_requires=[
          "httpx",
          "numpy"
      ],
      packages=['aioinflux3', ],
)
