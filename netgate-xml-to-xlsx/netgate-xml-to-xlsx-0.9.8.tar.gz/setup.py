# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['netgate_xml_to_xlsx',
 'netgate_xml_to_xlsx.plugins',
 'netgate_xml_to_xlsx.plugins.plugin_aliases',
 'netgate_xml_to_xlsx.plugins.plugin_ca',
 'netgate_xml_to_xlsx.plugins.plugin_cert',
 'netgate_xml_to_xlsx.plugins.plugin_cron',
 'netgate_xml_to_xlsx.plugins.plugin_dhcpd',
 'netgate_xml_to_xlsx.plugins.plugin_dhcpdv6',
 'netgate_xml_to_xlsx.plugins.plugin_diag',
 'netgate_xml_to_xlsx.plugins.plugin_dnshaper',
 'netgate_xml_to_xlsx.plugins.plugin_filter',
 'netgate_xml_to_xlsx.plugins.plugin_gateways',
 'netgate_xml_to_xlsx.plugins.plugin_haproxy',
 'netgate_xml_to_xlsx.plugins.plugin_hasync',
 'netgate_xml_to_xlsx.plugins.plugin_ifgroups',
 'netgate_xml_to_xlsx.plugins.plugin_installedpackages',
 'netgate_xml_to_xlsx.plugins.plugin_interfaces',
 'netgate_xml_to_xlsx.plugins.plugin_ipsec',
 'netgate_xml_to_xlsx.plugins.plugin_nat',
 'netgate_xml_to_xlsx.plugins.plugin_notifications',
 'netgate_xml_to_xlsx.plugins.plugin_ntpd',
 'netgate_xml_to_xlsx.plugins.plugin_openvpn',
 'netgate_xml_to_xlsx.plugins.plugin_ovpnserver',
 'netgate_xml_to_xlsx.plugins.plugin_ppps',
 'netgate_xml_to_xlsx.plugins.plugin_proxyarp',
 'netgate_xml_to_xlsx.plugins.plugin_rrd',
 'netgate_xml_to_xlsx.plugins.plugin_shaper',
 'netgate_xml_to_xlsx.plugins.plugin_snmpd',
 'netgate_xml_to_xlsx.plugins.plugin_sshdata',
 'netgate_xml_to_xlsx.plugins.plugin_staticroutes',
 'netgate_xml_to_xlsx.plugins.plugin_switches',
 'netgate_xml_to_xlsx.plugins.plugin_sysctl',
 'netgate_xml_to_xlsx.plugins.plugin_syslog',
 'netgate_xml_to_xlsx.plugins.plugin_system',
 'netgate_xml_to_xlsx.plugins.plugin_system_groups',
 'netgate_xml_to_xlsx.plugins.plugin_system_users',
 'netgate_xml_to_xlsx.plugins.plugin_unbound',
 'netgate_xml_to_xlsx.plugins.plugin_virtualip',
 'netgate_xml_to_xlsx.plugins.plugin_vlans',
 'netgate_xml_to_xlsx.plugins.plugin_widgets',
 'netgate_xml_to_xlsx.plugins.plugin_wizardtemp',
 'netgate_xml_to_xlsx.plugins.plugin_wol',
 'netgate_xml_to_xlsx.plugins.support']

package_data = \
{'': ['*']}

install_requires = \
['defusedxml>=0.7.1,<0.8.0',
 'lxml>=4.8.0,<5.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'toml>=0.10.2,<0.11.0',
 'xmltodict>=0.13.0,<0.14.0']

entry_points = \
{'console_scripts': ['flakeheaven = flakeheaven:entrypoint',
                     'netgate-xml-to-xlsx = netgate_xml_to_xlsx.main:main']}

setup_kwargs = {
    'name': 'netgate-xml-to-xlsx',
    'version': '0.9.8',
    'description': 'Translate Netgate firewall rules to spreadsheet for review.',
    'long_description': "# Netgate Firewall Converter\n\nThe `netgate-xml-to-xlsx` application converts a standard Netgate firewall .xml configuration file to an .xlsx spreadsheet with multiple tabs.\n\nWe've run the current implementation on a handful of our own XML firewall rules, however there's are probably some complex XML elements that will throw warnings when you run on your own files.\n\nIf you have a piece of XML that doesn't parse please extract a minimal portion (starting at the pfsense root) and open a ticket (better yet, modify the plugin and provide a pull request).\n\n## What is implemented?\n* First pass of XML elements in a base Netgate firewall installation.\n* Installed packages:\n  * haproxy\n\n## Requirements\n* Python 3.10+.\n* Netgate firewall XML version 21.x or 22.x.\n\n\n## Installation\n\nRecommend installing this with pipx:\n```\npipx install netgate-xml-to-xlsx\n```\n\nOr into a virtual environment.\n\n```\npython -m pip install netgate-xml-to-xlsx\n```\n\nOnce installed, the `netgate-xml-to-xlsx` command is available on your path.\n\n## Configuration file\n\nThe script requires a configuration file called `plugins.toml` in the current working directory when you run the script.\nDownload the sample from the GitLab [repository](https://gitlab.com/appropriate-solutions-inc/netgate-xml-to-xlsx/-/blob/main/plugins.toml).\nThe `plugins.toml` file defines the plugins to run as well as the order in which they are run.\nThe default order to to run all standard plugins in alphabetical order followed by the installed packages in alphabetical order.\n\n## Usage\n\n### Help\n\n```\n# Display help\nnetgate-xml-to-xlsx --help\n```\n\n### Sanitize Before Use\nNetgate configuration files contains sensitive information.\nThe XML file must be sanitized before processing.\nThe original (unsanitized) file is deleted.\n\n```\n# Sanitize Netgate configuration file(s) for review.\nnetgate-xml-to-xlsx --sanitize firewall-config.xml\nnetgate-xml-to-xlsx --sanitize dir/*.xml\n```\n\n### Convert to Spreadsheet\n* By default, output is sent to the `./output` directory.\n* Use the `--output-dir` parameter to set a specific output directory.\n* The output filename is the input filename with `.xlsx` attached to the end.\n\n```\n# Convert a Netgate firewall configuration file.\nnetgate-xml-to-xlsx firewall-config.xml\n\n# Convert all files in a directory.\nnetgate-xml-to-xlsx /fwalls/*-sanitized.xml\n```\n\n## Implementation Notes\n\n### Plugins\n\nEach top-level (or installed package) element is implemented in a separate plugin.\nThe plugin name matches the XML element being processed.\n\nSome advantages to implementing plugins:\n\n* Simplifies testing.\n  Plugins parse XML and return a list of rows to be output.\n  Plugins do not do their own output.\n  Test provide source XML and check the returned rows.\n* There are numerous Netgate plugins which I'll probably never see.\n  You can add your own plugins, along with tests.\n\n\n## Nosec on lxml imports\nThe `#nosec` flag is added to the lxml imports as the lxml parsing is not a security concern in this environment.\n\n## asserts\nAsserts are used throughout to:\n1. provide mypy guidance\n1. check for unexpected data as we're working from XML samples and not a specification.\n\n\n### Cookiecutter References\n* [cookiecutter-hypermodern-python](https://github.com/cjolowicz/cookiecutter-hypermodern-python)\n* [cookiecutter-poetry](https://fpgmaas.github.io/cookiecutter-poetry/)\n\n\n",
    'author': 'Raymond GA Côté',
    'author_email': 'ray@AppropriateSolutions.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/appropriate-solutions-inc/netgate-xml-to-xlsx',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
