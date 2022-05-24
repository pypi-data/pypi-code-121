from setuptools import setup, find_packages

with open("PyPI-README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='wzl-mqtt',
      version='2.5.1',
      url='https://git-ce.rwth-aachen.de/wzl-mq-public/iot/mqtt/',
      project_urls={
            "Bug Tracker": "https://git-ce.rwth-aachen.de/wzl-mq-public/iot/mqtt/-/issues",
      },
      author='Matthias Bodenbenner, Benjamin Montavon',
      author_email='m.bodenbenner@wzl-mq.rwth-aachen.de',
      description='Small library containing an MQTT publisher and receiver.',
      package_dir={'wzl': 'src'},
      packages=['wzl.mqtt'],
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      install_requires=['paho-mqtt==1.5.1'],
      python_requires='>=3.6',
      zip_safe=False)
