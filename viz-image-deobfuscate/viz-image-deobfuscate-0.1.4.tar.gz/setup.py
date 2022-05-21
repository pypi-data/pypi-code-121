# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['viz_image_deobfuscate']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.0,<10.0.0', 'piexif>=1.1.3,<2.0.0']

entry_points = \
{'console_scripts': ['image-deobfuscate-cli = viz_image_deobfuscate.cli:main']}

setup_kwargs = {
    'name': 'viz-image-deobfuscate',
    'version': '0.1.4',
    'description': 'Deobfuscate Viz-style manga images.',
    'long_description': '# Viz Manga Deobfuscator\n\nViz manga pages are delivered to the browser as obfuscated images and the client JS is responsible for deobfuscation of those images for the viewer to read. This program reproduces the deobfuscate logic to produce a readable image.\n\n`obfuscated image:`\n![obfuscated image](https://raw.githubusercontent.com/minormending/viz-image-deobfuscate/main/images/raw1.jpg)\n\n`deobfuscated image:`\n![deobfuscated image](https://raw.githubusercontent.com/minormending/viz-image-deobfuscate/main/images/page1.jpg)\n\nThe image Exif metadata stores a hex digest to deobfuscate the image. Using the each byte value of the digest with it\'s position in the digest, we can select the appropriate tile in the obfuscated image and put it in the proper place in the deobfuscated image.  \n\nDISCLAIMER: I am not licensed or affiliated with Viz Media and this repository is meant for informational purposes only.\n\n# Installation \n```\npip install viz-image-deobfuscate \n```\n\n# Usage\nThis package exposes `deobfuscate_image` that accepts a path to an image and returns an PIL `Image` of the deobfuscated image.\n\n```\nfrom viz_image_deobfuscate import deobfuscate_image\n\ndeobfuscated = deobfuscate_image("raw.jpg")\ndeobfuscated.save("page.jpg")\n```\n\n# CLI Usage\nBundled with this package is a CLI tool for scripting/testing purposes.\n\n```\nusage: image-deobfuscate-cli [-h] obfuscated_image deobfuscated_image\n\nDeobfuscate manage page image.\n\npositional arguments:\n  obfuscated_image    Path to the obfuscated image.\n  deobfuscated_image  Output path to the obfuscated image.\n\noptions:\n  -h, --help          show this help message and exit\n```\n\n## Example\n```\n>>> image-deobfuscate-cli raw1.jpg page1.jpg\n\nSuccessfully deobfuscated image at: page1.jpg\n```\n\n# Docker\nAlternatively, you can build your own docker container to run the CLI or download an already built container from [Docker Hub](https://hub.docker.com/r/minormending/viz-image-deobfuscate)\n\n```\n>>> docker build -t viz .\n>>> docker run -v /home/user/images/:/app/images viz images/raw1.jpg images/page1.jpg\n\nSuccessfully deobfuscated image at: images/page1.jpg\n```',
    'author': 'Kevin Ramdath',
    'author_email': 'krpent@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/minormending/viz-image-deobfuscate',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
