# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nicegui', 'nicegui.elements', 'nicegui.static.templates']

package_data = \
{'': ['*'],
 'nicegui': ['static/*'],
 'nicegui.elements': ['lib/*'],
 'nicegui.static.templates': ['css/*',
                              'highcharts/*',
                              'js/*',
                              'local/*',
                              'local/fontawesome/css/*',
                              'local/fontawesome/webfonts/*',
                              'local/ionicons/*',
                              'local/materialdesignicons/iconfont/*',
                              'local/robotofont/*',
                              'local/tailwind/*']}

install_requires = \
['Pygments>=2.9.0,<3.0.0',
 'asttokens>=2.0.5,<3.0.0',
 'docutils>=0.17.1,<0.18.0',
 'justpy==0.2.3',
 'markdown2>=2.4.0,<3.0.0',
 'matplotlib>=3.4.1,<4.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'typing-extensions>=3.10.0,<4.0.0',
 'uvicorn==0.17.6',
 'watchgod>=0.7,<0.8',
 'websockets==10.2']

setup_kwargs = {
    'name': 'nicegui',
    'version': '0.7.27',
    'description': 'Web User Interface with Buttons, Dialogs, Markdown, 3D Scences and Plots',
    'long_description': '<img src="https://raw.githubusercontent.com/zauberzeug/nicegui/main/sceenshots/ui-elements.png" width="300" align="right">\n\n# NiceGUI\n\nNiceGUI is an easy-to-use, Python-based UI framework, which renders to the web browser.\nYou can create buttons, dialogs, markdown, 3D scenes, plots and much more.\n\nIt is great for micro web apps, dashboards, robotics projects, smart home solutions and similar use cases.\nYou can also use it in development, for example when tweaking/configuring a machine learning algorithm or tuning motor controllers.\n\nNiceGUI is available as [PyPI package](https://pypi.org/project/nicegui/), [Docker image](https://hub.docker.com/r/zauberzeug/nicegui) and on [GitHub](https://github.com/zauberzeug/nicegui).\n\n[![PyPI version](https://badge.fury.io/py/nicegui.svg)](https://pypi.org/project/nicegui/)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/nicegui)](https://pypi.org/project/nicegui/)\n[![Docker Pulls](https://img.shields.io/docker/pulls/zauberzeug/nicegui)](https://hub.docker.com/r/zauberzeug/nicegui)<br />\n[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/zauberzeug/nicegui)](https://github.com/zauberzeug/nicegui/graphs/commit-activity)\n[![GitHub issues](https://img.shields.io/github/issues/zauberzeug/nicegui)](https://github.com/zauberzeug/nicegui/issues)\n[![GitHub forks](https://img.shields.io/github/forks/zauberzeug/nicegui)](https://github.com/zauberzeug/nicegui/network)\n[![GitHub stars](https://img.shields.io/github/stars/zauberzeug/nicegui)](https://github.com/zauberzeug/nicegui/stargazers)\n[![GitHub license](https://img.shields.io/github/license/zauberzeug/nicegui)](https://github.com/zauberzeug/nicegui/blob/main/LICENSE)\n\n## Features\n\n- browser-based graphical user interface\n- shared state between multiple browser windows\n- implicit reload on code change\n- standard GUI elements like label, button, checkbox, switch, slider, input, file upload, ...\n- simple grouping with rows, columns, cards and dialogs\n- general-purpose HTML and markdown elements\n- powerful high-level elements to\n  - plot graphs and charts,\n  - render 3D scenes,\n  - get steering events via virtual joysticks\n  - annotate images\n- built-in timer to refresh data in intervals (even every 10 ms)\n- straight-forward data binding to write even less code\n- notifications, dialogs and menus to provide state of the art user interaction\n- ability to add custom routes and data responses\n- capture keyboard input for global shortcuts etc\n- customize look by defining primary, secondary and accent colors\n\n## Installation\n\n```bash\npython3 -m pip install nicegui\n```\n\n## Usage\n\nWrite your nice GUI in a file `main.py`:\n\n```python\nfrom nicegui import ui\n\nui.label(\'Hello NiceGUI!\')\nui.button(\'BUTTON\', on_click=lambda: ui.notify(\'button was pressed\'))\n\nui.run()\n```\n\nLaunch it with:\n\n```bash\npython3 main.py\n```\n\nThe GUI is now available through http://localhost:8080/ in your browser.\nNote: The script will automatically reload the page when you modify the code.\n\nFull documentation can be found at [https://nicegui.io](https://nicegui.io).\n\n## Configuration\n\nYou can call `ui.run()` with optional arguments:\n\n- `host` (default: `\'0.0.0.0\'`)\n- `port` (default: `8080`)\n- `title` (default: `\'NiceGUI\'`)\n- `favicon` (default: `\'favicon.ico\'`)\n- `dark`: whether to use Quasar\'s dark mode (default: `False`, use `None` for "auto" mode)\n- `reload`: automatically reload the ui on file changes (default: `True`)\n- `show`: automatically open the ui in a browser tab (default: `True`)\n- `on_connect`: default function or coroutine which is called for each new client connection; the optional `request` argument provides session infos\n- `uvicorn_logging_level`: logging level for uvicorn server (default: `\'warning\'`)\n- `uvicorn_reload_dirs`: string with comma-separated list for directories to be monitored (default is current working directory only)\n- `uvicorn_reload_includes`: string with comma-separated list of glob-patterns which trigger reload on modification (default: `\'.py\'`)\n- `uvicorn_reload_excludes`: string with comma-separated list of glob-patterns which should be ignored for reload (default: `\'.*, .py[cod], .sw.*, ~*\'`)\n- `main_page_classes`: configure Quasar classes of main page (default: `\'q-ma-md column items-start\'`)\n- `binding_refresh_interval`: time between binding updates (default: `0.1` seconds, bigger is more cpu friendly)\n- `interactive`: used internally when run in interactive Python shell (default: `False`)\n\nThe environment variables `HOST` and `PORT` can also be used to configure NiceGUI.\n\n## Docker\n\nYou can use our [multi-arch Docker image](https://hub.docker.com/repository/docker/zauberzeug/nicegui) for pain-free installation:\n\n```bash\ndocker run --rm -p 8888:8080 -v $(pwd):/app/ -it zauberzeug/nicegui:latest\n```\n\nThis will start the server at http://localhost:8888 with the code from your current directory.\nThe file containing your `ui.run(port=8080, ...)` command must be named `main.py`.\nCode modification triggers an automatic reload.\n\n## Why?\n\nWe like [Streamlit](https://streamlit.io/) but find it does [too much magic when it comes to state handling](https://github.com/zauberzeug/nicegui/issues/1#issuecomment-847413651).\nIn search for an alternative nice library to write simple graphical user interfaces in Python we discovered [justpy](https://justpy.io/).\nWhile too "low-level HTML" for our daily usage it provides a great basis for "NiceGUI".\n\n## API\n\nThe API reference is hosted at [https://nicegui.io](https://nicegui.io) and is [implemented with NiceGUI itself](https://github.com/zauberzeug/nicegui/blob/main/main.py).\nYou may also have a look at [examples.py](https://github.com/zauberzeug/nicegui/tree/main/examples.py) for more demonstrations of what you can do with NiceGUI.\n\n## Abstraction\n\nNiceGUI is based on [JustPy](https://justpy.io/) which is based on the ASGI framework [Starlette](https://www.starlette.io/) and the ASGI webserver [Uvicorn](https://www.uvicorn.org/).\n\n## Deployment\n\nTo deploy your NiceGUI app, you will need to execute your `main.py` (or whichever file contains your `ui.run(...)`) on your server infrastructure.\nYou can either install the [NiceGUI python package via pip](https://pypi.org/project/nicegui/) on the server or use our [pre-built Docker image](https://hub.docker.com/r/zauberzeug/nicegui) which contains all necessary dependencies.\nFor example you can use this `docker run` command to start the script `main.py` in the current directory on port 80:\n\n```bash\ndocker run -p 80:8080 -v $(pwd)/:/app/ -d --restart always zauberzeug/nicegui:latest\n```\n\nThe example assumes `main.py` uses the port 8080 in the `ui.run` command (which is the default).\nThe `--restart always` makes sure the container is restarted if the app crashes or the server reboots.\nOf course this can also be written in a docker compose file:\n\n```yaml\nnicegui:\n  image: zauberzeug/nicegui:latest\n  restart: always\n  ports:\n    - 80:8080\n  volumes:\n    - ./:/app/\n```\n\nWhile it is possible to provide SSL certificates directly through NiceGUI (using [JustPy config](https://justpy.io/reference/configuration/)) we suggest to use a reverse proxy like [Traefik](https://doc.traefik.io/traefik/) or [NGINX](https://www.nginx.com/).\n',
    'author': 'Zauberzeug GmbH',
    'author_email': 'info@zauberzeug.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zauberzeug/nicegui',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
