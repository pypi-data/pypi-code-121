from distutils.core import setup
setup(
  name = 'noapicode',         # How you named your package folder (MyLib)
  packages = ['noapicode'],   # Chose the same as "name"
  version = '0.2',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Consume APIs. No code',   # Give a short description about your library
  author = 'noapicode.com',                   # Type in your name
  author_email = 'contact@noapicode.com',      # Type in your E-Mail
  url = 'https://gitlab.com/d8544/noapicode',   # Provide either the link to your github or to your website
  download_url = 'https://gitlab.com/d8544/noapicode/-/archive/0.03/noapicode-0.03.tar.gz',    # I explain this later on
  keywords = ['noapicode', 'no', 'api', 'code'],   # Keywords that define your package best
  install_requires=[
          'requests',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)