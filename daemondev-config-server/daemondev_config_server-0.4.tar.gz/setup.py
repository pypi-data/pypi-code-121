from distutils.core import setup
setup(
  name = 'daemondev_config_server',         # How you named your package folder (MyLib)
  packages = ['src/config_server'],   # Chose the same as "name"
  version = '0.4',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Config-Files downloader',   # Give a short description about your library
  author = '@daemondev',                   # Type in your name
  author_email = 'granlinux@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/daemondev/daemondev-config-server',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/daemondev/daemondev-config-server/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['config-server', 'daemondev', 'config-files'],   # Keywords that define your package best
  install_requires=["pyyaml"],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
