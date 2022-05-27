from setuptools import setup,find_packages

setup(name="arduino_rpi_taskmaster",
      version="0.1.2",
      description="This is a taskmaster python package made for learning how to build a package",
      author="Amalkrishna UR",
      author_email="example@gmail.com",
      packages=find_packages(),
      requires=["pyserial","sockets"],
      )
