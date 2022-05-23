from setuptools import setup, find_packages

setup(name='machinariurne',
      version='0.1',
      description='Tools & Classes Collection',
      long_description='Some implemented elements.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='cogs classes tools utils easy easies comfort шестерни классы инструменты лёгкость',
      url='https://github.com/vega0/python.machinarium',
      author='Nightmare a.k.a Aselock.',
      author_email='nightmare.flow0@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'markdown', 'requests',
          'selenium', '2captcha-python',
          'selenium-requests',
          'undetected_chromedriver',
          'nordvpn-switcher',
          'pyperclip', 'names',
          'virtualenv', 'Flask',
          'wikipedia', 'googletrans', 'numpy'
      ], include_package_data=True, zip_safe=False)
