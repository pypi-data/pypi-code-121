from distutils.core import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory/"README.md").read_text()
setup(
  name = 'AESRLib',
  packages = ['AESRLib'],
  version = 'v1.0',
  license ='MIT',
  description = 'Crypto package based on variable key leveraging combo of AES and Randomization!',
  long_description_content_type = 'text/markdown',
  long_description = long_description,
  python_requires=">=3.10",
  author = 'Shubham Chakraborty',
  author_email = 'cosmoscandium@gmail.com',
  url = 'https://github.com/me-yutakun/AESRLib',
  download_url = 'https://github.com/me-yutakun/AESRLib/archive/refs/tags/v1.0.tar.gz',
  keywords = ['AES', 'Random', 'base64'],
  install_requires=[
          'pycryptodome',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Security :: Cryptography',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.10',
  ],
)