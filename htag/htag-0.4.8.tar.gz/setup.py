# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['htag', 'htag.runners']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'htag',
    'version': '0.4.8',
    'description': 'GUI toolkit for building GUI toolkits (and create beautiful applications for mobile, web, and desktop from a single python3 codebase)',
    'long_description': '# HTag : "[H]TML Tag"\n\nThe descendant of [gtag](https://github.com/manatlan/gtag) ... but :\n\n * Not tied to [guy](https://github.com/manatlan/guy)\n * Able to be used in anything which can display html/js/css (pywebview, cefpython3, a browser, in [pyscript](https://pyscript.net/).... or [guy](https://github.com/manatlan/guy))\n * A **lot lot lot better and simpler** (better abstractions/code/concepts)\n * "intelligent rendering" (redraw only component on state changes)\n * and it runs in [pyscript](https://pyscript.net/) too ;-)\n\nIt\'s a GUI toolkit for building GUI toolkits ;-)\n\n[DEMO/TUTORIAL](https://htag.glitch.me/)\n\n[Changelog](changelog.md)\n\n[Available on pypi.org](https://pypi.org/project/htag/)\n\n**HTag** provides somes [`runners`](htag/runners) ootb. But they are just here, for the show. IRL: you should build your own, for your needs.\n\n## To have a look\n\nSee the [demo source code](https://github.com/manatlan/htag/blob/main/examples/demo.py)\n\nTo try it :\n\n    $ pip3 install htag pywebview\n    $ wget https://raw.githubusercontent.com/manatlan/htag/main/examples/demo.py\n    $ python3 demo.py\n\nThere will be docs in the future ;-)\n\n## ROADMAP to 1.0.0\n\n * rock solid (need more tests)\n * ~~top level api could change (Tag() -> create a Tag, Tag.mytag() -> create a TagBase ... can be a little bit ambiguous)~~\n * add a runner with WS with stdlib ? (not starlette!)\n * I don\'t really like the current way to generate js in interaction : need to found something more solid.\n * ~~the current way to initiate the statics is odd (only on real (embedded) Tag\'s) : should find a better way (static like gtag ?!)~~\n\n\n',
    'author': 'manatlan',
    'author_email': 'manatlan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/manatlan/htag',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
