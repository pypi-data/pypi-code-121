from distutils.core import setup
setup(
  name = 'Renogy_Battery',         
  packages = ['Renogy_Battery'],  
  version = '0.1',    
  license='MIT',        
  description = 'Designed to interface with the Renogy LFP100S line of batteries',   
  author_email = 'epfenni@gmail.com',     
  url = 'https://github.com/epfenninger',   
  download_url = 'https://github.com/epfenninger/Renogy_Battery/archive/refs/heads/main.zip',   
  keywords = ['Renogy', 'LFP100S', 'Modbus'],   
  install_requires=[           
          'minimalmodbus',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',  
    'Programming Language :: Python :: 3',     
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)