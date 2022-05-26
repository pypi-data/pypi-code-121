from setuptools import setup

with open('README.md') as f:
    readme = f.read()

setup(name='MSATwtdenoiser',
      version='0.0.6',
      description='Denoising a 2D signal based on wavelet',
      long_description=readme,
      long_description_content_type='text/markdown',
      url='https://github.com/ahsouri/MSATwtdenoiser',
      author='Amir Souri',
      author_email='ahsouri@gmail.com',
      license='MIT',
      packages=['MSATwtdenoiser'],
      install_requires=[
          'numpy','matplotlib','scipy','PyWavelets','opencv-python'
      ],
      zip_safe=False)
