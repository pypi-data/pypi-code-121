from setuptools import setup, find_packages

# Setting up
setup(
      # the name must match the folder name 'verysimplemodule'
      name="vizual",
      version="0.0.3",
      author="Hugo Dolan",
      author_email="<hugojdolan@gmail.com>",
      description="Web UI and decorator synatx for print statement debugging",
      long_description="See readme file",
      packages=['vizual'],
      entry_points={
            'console_scripts': [
                  'vizual = vizual.vizual:main',
            ],
      },
      # This needs to be changed on each new release
      url = 'https://github.com/hugo1005/vizual',
      download_url = 'https://github.com/hugo1005/vizual/archive/refs/tags/v3.tar.gz',
      include_package_data=True,
      install_requires=['Flask','requests','docopt','pandas','numpy'], # add any additional packages that
      # needs to be installed along with your package. Eg: 'caer'
      
      keywords=['python', 'debugging', 'webapp', 'visual'],
      classifiers= [
                    "Development Status :: 5 - Production/Stable",
                    "Intended Audience :: Developers",
                    "Programming Language :: Python :: 2",
                    "Programming Language :: Python :: 3",
                    "Operating System :: MacOS :: MacOS X",
                    "Operating System :: Microsoft :: Windows",
                    ]
      )
