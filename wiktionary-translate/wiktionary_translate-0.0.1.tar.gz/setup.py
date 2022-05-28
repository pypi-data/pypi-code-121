from distutils.core import setup
setup(
  name = 'wiktionary_translate',         # How you named your package folder (MyLib)
  packages = ['wiktionary_translate'],   # Chose the same as "name"
  version = '0.0.1',      # Start with a small number and increase it with every change you make
  license='mpl-2.0',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Get English translations of foreign word with Wiktionary',   # Give a short description about your library
  author = 'Marvin perzi',                   # Type in your name
  author_email = 'hashcod3@protonmail.com',      # Type in your E-Mail
  url = 'https://github.com/Persie0/wiktionary_translate',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/Persie0/wiktionary_translate/archive/refs/tags/v0.0.1.tar.gz',    # I explain this later on
  keywords = ['wiktionary', 'dictionary'],   # Keywords that define your package best
  install_requires=[
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',   # Again, pick a license
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
  ],
)