# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fourier_drawing']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.4,<2.0.0', 'opencv-python>=4.5.5,<5.0.0', 'pygame>=2.1.2,<3.0.0']

setup_kwargs = {
    'name': 'fourier-drawing',
    'version': '0.1.6',
    'description': '',
    'long_description': "# Use fourier transform to draw epicycles with your drawings.\n\nDraw a picture or sample one, press space, then watch an epic simulation of epicycles being drawned identically as your picture. Thanks the the fourier transform your drawing will be reproduced in a real-time simulation only using epicycles.\n\n# Demo\n\n![https://www.youtube.com/watch?v=86bYtJCwQ_o](https://cdn.discordapp.com/attachments/507519157387132940/808039024022257694/fourier.gif)\n# Install\n\n```sh\n#Clone the repository\ngit clone git@github.com:MarcPartensky/Fourier.git\ncd Fourier\n\n#Install requirements\npip install -r requirements.txt\n```\n\n# Usage\n\nPut your model image `image.png` in the `FourierImages` folder.\n\n* Option 1: Give image at launch.\n\n```sh\npython __main__.py image.png\n```\n\n* Option 2: Launch then give the image.\n\n```sh\npython __main__.py\n> image name:\n```\n\nThen give your image:\n\n```sh\n> image name:image.png\n```\n\n# Run with docker\n```sh\n# Replace the first occurence of 'FourierImages' by your custom image folder\n# Replace 'rodolphe.jpg' by your own image too\ndocker-compose run \\\n    -v ./FourierImages:/opt/FourierImages \\\n    --entrypoint './__main__.py rodolphe.jpg' \\\n    fourier\n```\n\n# Description\n\nThere are 3 modes in this program:\n\n* Mode 1: **Sampling**\nSample or draw a picture.\n\n* Mode 2: **Drawing**\nWatch the epicycles simulation which uses fourier transform.\n\n* Mode 3: **Display**\nGet the output image directly without waiting for the simulation.\n\n# Controls\n\n* `Space`: Switch to next mode.\n* `Enter`: Go back to the center.\n* `Up/Down/Right/Left Arrow`: Move arround.\n* `Right/Left Shift`: Zoom in or out.\n* `Quit/Escape`: Quit.\n* `Z`: Cancel last sample.\n* `R`: Remove all samples.\n* `S`: Save the fourier-coefficients.\n\n## Hide or Show the graphical components\nPress the following numbers to toggle:\n* `1`: Image\n* `2`: Green lines\n* `3`: Red graph\n* `4`: White vectors\n* `5`: Grey circles\n* `6`: Yellow sample\n\n# Enjoy!\n",
    'author': 'Marc Partensky',
    'author_email': 'marc.partensky@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/marcpartensky/fourier',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
