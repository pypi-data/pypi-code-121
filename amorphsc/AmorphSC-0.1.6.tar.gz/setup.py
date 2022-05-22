from distutils.core import setup

setup(
  name = 'AmorphSC',         # How you named your package folder (MyLib)
  packages = ['AmorphSC'],   # Chose the same as "name"
  version = '0.1.6',      # Start with a small number and increase it with every change you make
  license='GNU',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Package to permorm data analysis on amorphous semiconductors',   # Give a short description about your library
  author = 'Luca Fabbri',                   # Type in your name
  author_email = 'luca.fabbri98@outlook.it',      # Type in your E-Mail
  url = 'https://github.com/lfabbri98/AmorphSC',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['semiconductors', 'amorphous', 'KPFM', 'AFM','photocurrent'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pandas',
          'matplotlib',
          'scipy',
          'numpy',
      ],
)