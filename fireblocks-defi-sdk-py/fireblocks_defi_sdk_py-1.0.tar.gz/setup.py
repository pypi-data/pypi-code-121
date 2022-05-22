from distutils.core import setup
setup(
    name='fireblocks_defi_sdk_py',
    packages=['fireblocks_defi_sdk_py'],
    version='1.0',
    license='MIT',
    description = 'fireblocks_defi_sdk_py',
    author = 'Fireblocks',
    author_email = 'fireblocks@fireblocks.com',
    url = 'https://github.com/fireblocks/fireblocks-defi-sdk-py',   # Provide either the link to your github or to your website
    download_url = 'https://github.com/fireblocks/fireblocks-defi-sdk-py/archive/refs/tags/1.0.tar.gz',
    keywords = ['FIREBLOCKS', 'DeFi', 'SDK', 'PYTHON'],   # Keywords that define your package best

    install_requires=[
          'fireblocks_sdk',
          'web3',
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
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    ],
)
