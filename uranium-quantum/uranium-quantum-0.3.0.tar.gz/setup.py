from distutils.core import setup
from os import path

try:
  this_directory = path.abspath(path.dirname(__file__))
  with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
      long_description = f.read()
except:
  long_description = "Support libraries for the Uranium quantum computing platform (https://uranium.transilvania-quantum.org/)."

setup(
  name = 'uranium-quantum',
  packages = ['uranium_quantum/circuit_composer', 'uranium_quantum/circuit_exporter'],  
  version = '0.3.0',
  license='MIT',
  description = 'Support libraries for the Uranium quantum computing platform (https://uranium.transilvania-quantum.org/).',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author = 'Radu Marginean',
  author_email = 'radu.marg@gmail.com',
  url = 'https://github.com/radumarg/uranium-quantum',
  download_url = 'https://github.com/radumarg/uranium-quantum/releases/tag/v0.2.5',
  keywords = ['quantum', 'computing', 'uranium platform'],  
  install_requires=[            
          'click',
          'pyyaml'
      ],
  classifiers=[
    # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" 
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
  ],
)
