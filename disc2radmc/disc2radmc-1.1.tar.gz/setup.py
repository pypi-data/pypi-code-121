from setuptools import setup
setup(
    name = 'disc2radmc',         # How you named your package folder (MyLib)
    packages = ['disc2radmc'],   # Chose the same as "name"
    version = '1.1',      # Start with a small number and increase it with every change you make
    license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description = 'Disc2radmc is a package to create parametric models of debris discs that can be fed into RADMC3D and simulate images of dust and gas emission.',   # Give a short description about your library
    author = 'Sebastian Marino',                   # Type in your name
    author_email = 'sebastian.marino.estay@gmail.com',      # Type in your E-Mail
    url = 'https://github.com/SebaMarino/disc2radmc',   # Provide either the link to your github or to your website
    download_url = 'https://github.com/SebaMarino/disc2radmc/archive/refs/tags/v1.1.tar.gz',    #
    keywords = ['radiative transfer', 'debris disc', 'radmc3d', 'circumstellar disc'],   # Keywords that define your package best
    install_requires=[
        'numpy',
        'matplotlib',
        'astropy',
        'cma',
        'scipy'],
    include_package_data=False,
    classifiers=[
        'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        'Programming Language :: Python :: 2.7',    #Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3',      
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
  ],
)
