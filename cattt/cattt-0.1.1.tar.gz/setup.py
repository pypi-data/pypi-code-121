# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cattt']

package_data = \
{'': ['*']}

extras_require = \
{':extra == "glfw"': ['glfw>=2.5.3,<3.0.0'],
 ':extra == "glfw" or extra == "sdl"': ['skia-python>=87.4,<88.0',
                                        'darkdetect>=0.5.1,<0.6.0'],
 ':extra == "sdl"': ['glcontext>=2.3.6,<3.0.0'],
 'glfw': ['PyOpenGL>=3.1.5,<4.0.0'],
 'sdl': ['PySDL2>=0.9.11,<0.10.0', 'zengl>=1.2.2,<2.0.0']}

setup_kwargs = {
    'name': 'cattt',
    'version': '0.1.1',
    'description': 'Cattt is a pure Python cross-platform UI framework',
    'long_description': '# :cat: Cattt\nCattt (kˈæt) is a pure Python cross-platform UI framework.\n\n[Documentation Site](https://i2y.github.io/cattt)\n\n## Goals\nThe primary final goal of Cattt is to provide features for Python programmers easy to create a GUI application for several OS platforms and web browsers in a single most same code as possible as. The second goal is to provide a UI framework that Python programmers can easily understand, modify, and extend as needed.\n(Stated on May 25, 2022: This goal is the final goal. Currently this framework is in the super early stage, so this goal is far away. I hope to get much closer to the goal in a few months or a year by improving the implementation or documentation a little bit every day as much as possible.)\n\n## Features\n- The core part as a UI framework of Cattt is written in only Python. It\'s not a wrapper for existing something written in other programing languages.\n- Cattt allows human to define UI declaratively in Python.\n- Cattt provides hot-reloading or hot-restarting on development.\n- Dark mode is supported. If the runtime environment is in dark mode, Cattt app\'s UI appearance will automatically be styled in dark mode. The default color scheme for light and dark mode might be very like the one of GitHub.\n- Cattt utilizes GPU via dependent libraries.\n\n## Dependencies\n- For desktop platforms, Cattt is standing on existing excellent python bindings for window management library (GLFW or SDL2) and 2D graphics library (Skia).\n- For web browsers, Cattt is standing on awesome Pyodide/PyScript and CanvasKit (Wasm version of Skia).\n\n## Installation\nhttps://i2y.github.io/cattt/getting-started/\n\n## An example of code using Cattt\n```python\nfrom cattt.core import App, Button, Column, Component, Row, State, Text\nfrom cattt.frame import Frame\n\n\nclass Counter(Component):\n    def __init__(self):\n        super().__init__()\n        self._count = State(0)\n\n    def view(self):\n        return Column(\n            Text(self._count),\n            Row(Button("Up").on_click(self.up), Button("Down").on_click(self.down)),\n        )\n\n    def up(self, _):\n        self._count += 1\n\n    def down(self, _):\n        self._count -= 1\n\n\nApp(Frame("Counter", 800, 600), Counter()).run()\n```\n\nhttps://user-images.githubusercontent.com/6240399/169688790-f020be7e-5b6b-456e-8620-f09ad3ba0a27.mp4\n\nYou can see some other examples in [examples](examples) directory.\n\n## Supported Platforms\nCurrently, Cattt theoretically should support not-too-old versions of the following platforms.\n\n- Windows 10/11\n- Mac OS X\n- Linux\n- Web browsers\n\nUnfortunately, however, I could not actually confirm this at all on Linux, as I don\'t have a Linux machine these days. I want it..\nAlso, currently I have a only windows machine and it had already been updated to Windows 11, so I now confirm only it on Windows 11.\nSo, If anyone have an environment other than Windows 11, it would be helpful if you could try it and report back to me if you have any problems. If you find any problems, it would be more helpul if you could fix it.\n\n## License\nMIT License\n\nCopyright (c) 2022 Yasushi Itoh\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n',
    'author': 'Yasushi Itoh',
    'author_email': 'i2y@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/i2y/cattt',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
