from setuptools import setup
import setuptools

setup(
      name='EXP_jangddol',
      version='1.1.5',
      url='https://github.com/jangddol/EXP_jangddol_pip.git',
      description='kawaii experiment data analysis tool',
      author='jangddol',
      author_email='j991005@korea.ac.kr',
      packages=setuptools.find_packages(),
      install_requires=[
          'uncertainties==3.1.6',
          'matplotlib==3.5.0',
          'numpy==1.21.0'
      ],
      classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
      ],
)