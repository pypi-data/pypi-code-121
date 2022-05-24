from distutils.core import setup

setup(
  name = 'riversim',         # How you named your package folder (MyLib)
  packages = ['riversim'],   # Chose the same as "name"
  version = '0.3',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Simulation of river growth using model based on Laplace equation. Mathematicaly, in this program we solve PDE equation using Finite Element Method(FEM).',   # Give a short description about your library
  author = 'OLEG KMECHAK',                   # Type in your name
  author_email = 'oleg.kmechak@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/okmechak/riversimpy',   # Provide either the link to your github or to your website
  download_url = '',#'https://github.com/okmechak/riversimpy/archive/refs/tags/v0.2.tar.gz',    # I explain this later on
  keywords = ['LAPLACEA', 'RIVER', 'FEM', 'HARMONIC', 'NETWORK', 'GROWTH', 'SIMULATION'],   # Keywords that define your package best
  install_requires=[]  ,
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.8',
  ],
  package_data = {'riversim': ['*.so']},
)