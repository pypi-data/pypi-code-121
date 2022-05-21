# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['linkhub_prometheus_exporter']

package_data = \
{'': ['*']}

install_requires = \
['dynaconf>=3.1.8,<4.0.0',
 'jsonrpcclient>=4.0.2,<5.0.0',
 'prometheus-client>=0.14.1,<0.15.0',
 'requests>=2.27.1,<3.0.0',
 'types-requests>=2.27.25,<3.0.0']

entry_points = \
{'console_scripts': ['linkhub_exporter = '
                     'linkhub_prometheus_exporter.exporter:main']}

setup_kwargs = {
    'name': 'linkhub-prometheus-exporter',
    'version': '0.4.0',
    'description': 'A Prometheus metrics exporter for Alcatel Linkhub 4G router boxes',
    'long_description': '# Linkhub Exporter\n\nA Prometheus exporter for Alcatel Linkhub boxes.\n\nTested with an Alcatel HH41 4G LTE hotspot WiFi router.\n\n![Alcatel HH41 product info](docs/linkhub_product.jpg)\n\n## Usage\n\nInstall Poetry for you system (need `>=1.2.0b1` currently if using\nthe dynamic versioning, and have to add the relevant plugin with\n`poetry plugin add poetry-dynamic-versioning-plugin`). Then install the\npackage with:\n\n```shell\npoetry install\n```\n\nYou\'ll need a Request Key to run exporter, which is derived from the\nlogin password of router box admin interface. See below how to\nobtain it.\n\nOnce you have a key, you can set it in multiple ways:\n\n* In `.secrets.toml`, see the template shipped at `secrets.toml.template`\n  for the format (note the `.` for the non-template filename), OR\n* Set an environment variable `LINKHUB_REQUEST_KEY` with the value, e.g.\n  `export LINKHUB_REQUEST_KEY=...` in your shell where `...` is replaced with\n  the actual value.\n\nThen start up the exporter:\n\n```shell\npoetry run exporter\n```\n\n### Running in Docker\n\nBuild the image with the included Dockerfile from the cloned repository,\nlet\'s say:\n\n```shell\ndocker build -t linkhub_exporter\n```\n\nand then run the resulting image as:\n\n```shell\ndocker run -ti --rm -e "LINKHUB_REQUEST_KEY=...." -p 9877:9877 linkhub_exporter\n```\n\nwhich exposes the Prometheus metrics on `http://localhost:9877`. Don\'t forget\nto set the `LINKHUB_REQUEST_KEY` value, or add it in an `.env` file and\nrun things as:\n\n```shell\ndocker run -ti --rm --env-file .env -p 9877:9877 linkhub_exporter\n```\n\n### Running in Docker Compose\n\nYou can add this exporter as a container in your `docker-compose.yml`, along\nsimilar lines (other container configuration has been snip\'d):\n\n```yaml\n  linkhub:\n    image: imrehg/linkhub_prometheus_exporter\n    restart: always\n    ports:\n      - "9877:9877"\n    environment:\n      - LINKHUB_EXPORTER_ADDRESS=\'0.0.0.0\'\n    env_file:\n      - .env\n```\n\nThe `LINKHUB_REQUEST_KEY` value should be set in the `.env` file (or wherever\nyou will keep the configuration for this particular service). You can comment\nout the `ports` section if you don\'t want to view the results outside of the\ndocker compose run services. You might want to add `network` field if you\nare running things within a custom network.\n\nFinally, you probably want to set an explicit tag for the image value.\n\n### Setting up task in Prometheus\n\nThe setup in Prometheus is pretty straightforward, using the relevant IP/port\ncombo. If the server is run manually or through Docker on its own, use the machine\'s\nIP that\'s running it, and the port that is set in the config. If docker compose\nis used, the can use the service name to connect to it automatically, say like this:\n\n```yaml\n  - job_name: \'linkhub\'\n    scrape_interval: 5s\n    static_configs:\n      - targets: [\'linkhub:9877\']\n```\n\n(The other parts of the Prometheus configuration are omitted.)\n\n### Getting the request key\n\nCurrently the easiest way to get it is to:\n\n* Open a browser  and navigate to your router admin interface\n* Open the debug console, and ensure that network requests are logged there\n* Log in to the admin interface\n* Check requests going to `webapi`, look for the requests headers, and the\n  value of the `_TclRequestVerificationKey` is what you should use for the\n  request key setting of this exporter.\n\n\n### Showing the metrics in Grafana\n\nAn [example Grafana dashboard](extra/Grafana_Sammple_LinkHub_Metrics.json)\nsetup is provided in the `extra` folder.\n\n![Grafana dashboard screenshot part 1](docs/grafana_screenshot1.png)\n\n![Grafana dashboard screenshot part 2](docs/grafana_screenshot2.png)\n\n## License\n\nCopyright 2022 Gergely Imreh <gergely@imreh.net>\n\nLicensed under the Apache License, Version 2.0 (the "License");\nyou may not use this file except in compliance with the License.\nYou may obtain a copy of the License at\n\n    http://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.',
    'author': 'Gergely Imreh',
    'author_email': 'gergely@imreh.net',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/imrehg/linkhub_prometheus_exporter',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
