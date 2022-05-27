# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lovesay']

package_data = \
{'': ['*']}

install_requires = \
['typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['lovesay = lovesay.cli:main']}

setup_kwargs = {
    'name': 'lovesay',
    'version': '0.3.2',
    'description': 'Cowsay, but full of love',
    'long_description': '<h2 align="center"> ━━━━━━  ❖  ━━━━━━ </h2>\n\n<!-- BADGES -->\n<div align="center">\n   <p></p>\n   \n   <img src="https://img.shields.io/github/stars/zenithds/lovesay?color=F8BD96&labelColor=302D41&style=for-the-badge">   \n\n   <img src="https://img.shields.io/github/forks/zenithds/lovesay?color=DDB6F2&labelColor=302D41&style=for-the-badge">   \n\n   <img src="https://img.shields.io/github/repo-size/zenithds/lovesay?color=ABE9B3&labelColor=302D41&style=for-the-badge">\n   \n   <img src="https://badges.pufler.dev/visits/zenithds/lovesay?style=for-the-badge&color=96CDFB&logoColor=white&labelColor=302D41"/>\n   <br>\n</div>\n\n<p/>\n\n---\n\n### ❖ Information \n\n  lovesay is a simple python script that displays a quote from a loved one based on the day of the month or a quote passed in through the cli arguments. \n\n  <img src="assets/lovesay.gif" alt="lovesay gif">\n\n---\n\n### ❖ Requirements\n\nNote: These requirements only apply if using you\'re using lovesay to print a different quote for each day of the month.  \n\n- A quotes file stored in `$HOME/.config/lovesay/`\n- Each quote must be on a new line, see the example quotes file in `.config/lovesay/quotes`\n- (optional) A partner to write you 31 lines full of love, one for each day of the month\n\n---\n\n### ❖ Installation\n\n> Install from pip\n```sh\npip3 install lovesay\n```\n\n> Install from source\n- First, install [poetry](https://python-poetry.org/)\n```sh\ngit clone https://github.com/ZenithDS/lovesay.git\ncd lovesay\npoetry build\npip3 install ./dist/lovesay-0.3.1.tar.gz\n```\n\n### ❖ Usage \n\nlovesay can be used in a similar fashion to cowsay\n\n```sh\nlovesay "Hello World"\n```\n\nif there\'s a `quotes` file in `$HOME/.config/lovesay/`, lovesay can be used without any arguments\n\n```sh\nlovesay\n```\n\nif you\'d like to use a quotes stored somewhere other than the path above, the `LOVESAY_PATH` env variable can be used as such\n\n```sh\nexport LOVESAY_PATH="~/path/to/file"\n```\n\nlovesay can also be used with a variety of different color schemes.\n\n> lovesay uses [catppuccin](https://github.com/catppuccin) as it\'s default color scheme, but a different one can be specified using the `--color` option. \n\nFor example:\n```sh\nlovesay # uses catppuccin\n```\n  \n```sh\nlovesay -c nord # uses nord \n```\n\nSupported color schemes as of now: \n- [catppuccin](https://github.com/catppuccin)\n- [nord](https://github.com/arcticicestudio/nord)\n- [dracula](https://github.com/dracula/dracula-theme)\n- [gruvbox](https://github.com/morhetz/gruvbox)\n- [onedark](https://github.com/joshdick/onedark.vim)\n- [tokyonight](https://github.com/folke/tokyonight.nvim)\n- [rose pine](https://rosepinetheme.com/)\n- [ayu](https://github.com/ayu-theme)\n- [palenight](https://github.com/drewtempelmeyer/palenight.vim)\n- [gogh](https://github.com/Mayccoll/Gogh)\n\nby default, lovesay checks for the quotes file at `$HOME/.config/lovesay/quotes` if there is nothing there and no quote is given using the cli args, it will just print out a heart with no quote\n\n---\n\n### ❖ About lovesay\n\nI wrote lovesay because I got tired of seeing neofetch or pfetch every time I opened my terminal. I wanted something more personal. \n\nSeeing words full of love from my partner is a lot better than any other command I could possibly run. It makes my terminal feel cozy, welcoming, and as is the case with most things my partner touches, it makes my terminal feel like home. \n\nI hope that someone else finds a use for this little script as well. Love is a wonderful thing, and we could all use a little bit more of it in our lives (especially arch linux users)\n\n---\n\n### ❖ What\'s New? \n0.3.2 - FEAT: Specify alternative path to quotes file using env variable\n\n---\n\n<div align="center">\n\n   <img src="https://img.shields.io/static/v1.svg?label=License&message=MIT&color=F5E0DC&labelColor=302D41&style=for-the-badge">\n\n</div>\n',
    'author': 'ZenithDS',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
