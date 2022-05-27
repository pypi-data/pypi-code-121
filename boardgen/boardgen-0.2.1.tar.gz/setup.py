# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['boardgen',
 'boardgen.core',
 'boardgen.models',
 'boardgen.readme',
 'boardgen.shapes',
 'boardgen.shapes.label']

package_data = \
{'': ['*'],
 'boardgen': ['res/*', 'res/boards/*', 'res/shapes/*', 'res/templates/*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'devtools>=0.8.0,<0.9.0',
 'pydantic>=1.9.0,<2.0.0',
 'svgwrite>=1.4.2,<2.0.0']

entry_points = \
{'console_scripts': ['boardgen = boardgen.cli:cli']}

setup_kwargs = {
    'name': 'boardgen',
    'version': '0.2.1',
    'description': 'Board pinout diagram generator',
    'long_description': '# boardgen\n\nAutomagically generate beautiful Adafruit-like pinout diagrams for IoT boards ✨\n\n## Introduction\n\nBoardgen allows to generate vector images, containing pinout diagrams for any IoT module. The images are inspired by Adafruit\'s great, well-recognized pinouts, and look like this one:\n\n![demo](.github/wr3-demo.png)\n\nIt is a Python tool that uses simple JSON files for defining shapes, colors, pin layouts and numbers. These files are then processed and drawn onto a .SVG image.\n\nDefining new boards is fully done in JSON and doesn\'t require Python programming, nor SVG knowledge.\n\n## Usage\n\nBoardgen can be used as a library (see [cli.py](boardgen/cli.py) for an example) or with its built-in CLI program.\n\n1. `pip install boardgen`\n2. `boardgen --help`\n3. `boardgen list boards` to get a list of available boards\n4. `boardgen draw <board name>` to produce an image file in your working directory\n\n```\nUsage: boardgen [OPTIONS] COMMAND [ARGS]...\n\n  boardgen CLI v0.1.0\n\nOptions:\n  --boards TEXT     Custom boards directories\n  --shapes TEXT     Custom shapes directories\n  --templates TEXT  Custom templates directories\n  --presets TEXT    Custom presets .json\n  --roles TEXT      Custom roles .json\n  --flash TEXT      Custom flash regions .json\n  --help            Show this message and exit.\n\nCommands:\n  draw  Draw board diagrams\n  list  List boards/templates/etc\n```\n\n### Board definitions\n\nWriting board definitions means putting a .JSON file to a directory and specifying this directory using the `--boards` option.\n\nBoardgen is meant to be used with PlatformIO-style board definition files. An example of such a board can be found [here (libretuya/boards/wr3.json)](https://github.com/kuba2k2/libretuya/blob/master/boards/wr3.json).\n\nNote that the board manifest uses `"_base"` definitions. These are merged recursively with the manifest, and this result is expected to produce a complete file.\n\nApart from PlatformIO default variables (such as `build`, `debug`, `upload` or `name`, `url` and `vendor`) the board definition contains a [`Pcb`](boardgen/models/pcb.py) object.\n\n### Templates\n\nA [`Template`](boardgen/models/template.py) is a JSON object containing lists of shapes for each side of a PCB. Additionally, it contains a mapping of pin names to shape IDs to allow automatic alignment of pinout labels.\n\n```json\n{\n\t"name": "demo-template",\n\t"title": "Demo template",\n\t"width": 10,\n\t"height": 20,\n\t"front": [\n\t\t{"info": "List of front side shapes goes here"},\n\t\t{\n\t\t\t"comment": "this is a sample rectangle",\n\t\t\t"id": "shape1",\n\t\t\t"type": "rect",\n\t\t\t"pos": "0,0",\n\t\t\t"size": "10,20",\n\t\t\t"fill": {"color": "black"}\n\t\t}\n\t],\n\t"back": [],\n\t"pads": {\n\t\t"1": "demo-template.front.shape1",\n\t\t"2": "demo-template.front.shape2",\n\t\t"3": "demo-template.front.shape3",\n\t\t"4": "demo-template.front.shape4",\n\t}\n}\n```\n\n### Shapes\n\nA shape JSON file is an array of multiple shape objects. Including shape JSON files is possible. For example, to include `my-shape.json`:\n\n```json\n{\n\t"name": "my-shape",\n\t"id": "id-of-my-shape",\n\t"pos": "5,10"\n}\n```\n\nEach shape is a JSON object, which has a common set of attributes:\n- `pos` - REQUIRED: defines the anchor of a shape (in milimeters)\n- `preset` (or a `presets` array) - used to merge the shape object with a [preset object](boardgen/res/presets.json) (see "boardgen list presets")\n- `id` - used to refer to the shape\'s anchor from the `pads` mapping\n- `vars` - mapping of variables for `${VAR}` substitution, optional\n\n#### Rectangles\n\n- `type`: must be `"rect"`\n- `pos`: REQUIRED: rectangle top-left corner position\n- `size`: REQUIRED: rectangle size ("width,height") in milimeters\n- `fill`: see FillStyle below\n- `stroke`: see FillStyle below\n- `rx`: X corner radius\n- `ry`: Y corner radius\n\n#### Circles\n\n- `type`: must be `"circle"`\n- `pos`: REQUIRED: circle center position\n- `d`: diameter (milimeters), OR:\n- `r`: radius (milimeters) - one of `d` and `r` is required\n- `fill`: see FillStyle below\n- `stroke`: see FillStyle below\n\n#### Text\n\n- `type`: must be `"text"`\n- `pos`: REQUIRED: text center position\n- `font_size`: REQUIRED: font size\n- `text`: REQUIRED: string to draw\n- `fill`: see FillStyle below\n\n#### FillStyle\n\n- `color`: string (color name, HTML hex), fill/stroke color\n- `lgrad`: linear gradient as a list ["x,y", "color", "x,y", "color"]\n  - 1st stop position\n  - 1st stop color\n  - 2nd stop position\n  - 2nd stop color\n- `width`: stroke width (not used for "fill")\n\n## Support\n\nAs this project is just a quick solution that\'ll be used in [LibreTuya](https://github.com/kuba2k2/libretuya) for generating pinouts, it\'s not really well documented. If you find this project interesting and need any help using it, feel free to open an issue and I\'ll try to provide more examples and info on how to use it.\n',
    'author': 'Kuba Szczodrzyński',
    'author_email': 'kuba@szczodrzynski.pl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
