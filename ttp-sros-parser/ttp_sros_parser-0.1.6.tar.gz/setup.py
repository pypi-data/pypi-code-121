# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ttp_sros_parser', 'ttp_sros_parser.templates']

package_data = \
{'': ['*'],
 'ttp_sros_parser.templates': ['admin_display_file/*',
                               'custom/*',
                               'full_config/*',
                               'helpers/*',
                               'show_commands/*']}

install_requires = \
['ttp==0.7.2']

setup_kwargs = {
    'name': 'ttp-sros-parser',
    'version': '0.1.6',
    'description': 'Utility to parse a full SROS Configuration.',
    'long_description': '[![codecov](https://codecov.io/gh/h4ndzdatm0ld/ttp_sros_parser/branch/main/graph/badge.svg?token=ZL8JDKLQJI)](https://codecov.io/gh/h4ndzdatm0ld/ttp_sros_parser)\n\n# TTP SrosParser\n\nA library to parse a Nokia SROS 7750 full hierarchical configuration text file into structured data. Show commands are also able to be parsed, if included in the file alongside the configuration. This library is still under development, but a lot of parsers are readily available (see below for supported features). Configurations used for testing have all been on release version higher than TiMOS 16. At the moment, there is no capability to specify release version to accommodate different parsing templates.\n\n## What TTP SrosParser is not\n\nA library that connects and extracts information from a remote device. You, as the end-user must obtain a text file of the configuration. This file will be passed into the SrosParser class and you are able to convert a flat text configuration file into structure data using the built-in TTP parser templates. At this point, it\'s recommended to use a new instance of the srosparser with an individual show command as the text to parse to get the best results when parsing a show commands.\n\n## Example\n\n```python\n"""SrosParser - Example."""\nfrom ttp_sros_parser.srosparser import SrosParser\n\nEXAMPLE_CONFIG = "some/dir/path/to/7750-config.txt"\n\n# Instantiate class\nrouter = SrosParser(EXAMPLE_CONFIG)\n\n# Call `get_system_cards` method\nrouter.get_system_cards()\n```\n\nResults:\n\n```json\n[\n   {\n      "configure":{\n         "card":{\n            "card-type":{\n               "card-type":"iom-1",\n               "subscription-level":"cr"\n            },\n            "fail-on-error":true,\n            "mda":{\n               "admin-state":true,\n               "egress-xpl":{\n                  "window":"10"\n               },\n               "fail-on-error":true,\n               "ingress-xpl":{\n                  "window":"10"\n               },\n               "mda-slot":"1",\n               "mda-type":"me6-100gb-qsfp28"\n            },\n            "slot-number":"1"\n         }\n      }\n   }\n]\n```\n\n## Available Methods (Parsers)\n\nCurrent methods available (Automatically updated at build):\n\n[Methods](docs/methods.md)\n\n## Full Config\n\n**SrosParser** allows you to parse the full configuration with a single method call, `get_full_config()` and receive the full JSON output of the device.\n\n## Custom Templates\n\nSrosParser allows you to simply specify a custom template after you initialize a new class object.\n\n```python\nrouter = SrosParser("path/to/config.txt")\n\ncool_ttp_template = router.get_custom_template("path/to/template")\n\nprint(cool_ttp_template)\n```\n\n## Contributing\n\nAny contribution to the project must include unit tests and pass all linting.\n\nSimply run:\n\n- `docker-compose build`\n- `docker-compose run test`\n',
    'author': 'Hugo',
    'author_email': 'hugotinoco@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/h4ndzdatm0ld/ttp_sros_parser',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
