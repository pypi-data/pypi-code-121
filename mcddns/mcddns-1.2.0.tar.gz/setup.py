# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mcddns', 'mcddns.provider']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.23,<2.0', 'requests>=2.27,<3.0']

entry_points = \
{'console_scripts': ['mcddns = mcddns.cli:main']}

setup_kwargs = {
    'name': 'mcddns',
    'version': '1.2.0',
    'description': 'Industrial-strength dynamic DNS client',
    'long_description': "# MCDDNS\n\n[![Continuous Integration](https://github.com/mconigliaro/mcddns/actions/workflows/ci.yml/badge.svg)](https://github.com/mconigliaro/mcddns/actions/workflows/ci.yml)\n\n**M**ike **C**onigliaro's industrial-strength **D**ynamic **D**omain **N**ame **S**ystem client\n\n## Features\n\n- Extensible plugin-oriented architecture with a simple API\n  - Address providers are responsible for obtaining an address\n  - DNS providers are responsible for managing a DNS record\n- Resilient against network and endpoint failures\n  - Built-in result validation for address providers\n  - Use multiple address providers (keep trying until one succeeds)\n  - Optional retry with Fibonacci backoff\n  - Cron mode (prevents email flood if your Internet connections goes down)\n- Detailed logging\n- Dry-run mode (shows what will happen without changing anything)\n\n### Built-In Providers\n\n#### Address Providers\n\n- `aws.CheckIP`: Obtains a public IPv4 address via [Amazon Web Services](https://aws.amazon.com/)\n- `dyn.CheckIP`: Obtains a public IPv4 address via [Dyn](https://dyn.com/)\n- `google.CheckIP`: Obtains a public IPv4 address via [Google Domains](https://domains.google.com)\n- `ipify.IPv4`: Obtains a public IPv4 address via [ipify](https://www.ipify.org/)\n- `ipify.IPv6`: Obtains an IPv6 address via [ipify](https://www.ipify.org/)\n\n#### DNS Providers\n\n- `aws.Route53`: Manages records in [Amazon Route53](https://aws.amazon.com/route53/)\n\n## Installation\n\n    pip install mcddns\n\n## Running the Application\n\n    mcddns <dns_provider> <fqdn> [options]\n\nUse `--help` to see available options.\n\n## Development\n\n### Getting Started\n\n    poetry install\n    poetry shell\n    ...\n\n### Running Tests\n\n    pytest\n\n### Writing Providers\n\nA provider is any class that inherits from `AddressProvider` or `DNSProvider`. In production mode, Python modules/packages prefixed with `mcddns_` will automatically be imported from the following locations:\n\n1. `$XDG_CONFIG_HOME/mcddns/provider`\n1. `/etc/mcddns/provider`\n1. [sys.path](https://docs.python.org/3/library/sys.html#sys.path)\n\nExample: If you create a file at `$XDG_CONFIG_HOME/mcddns/provider/mcddns_foo.py` with a class named `Bar` that inherits from one of the `Provider` subclasses, your module can be referenced (e.g. in command-line options) as `foo.Bar`.\n\n#### Provider Methods\n\nEach provider type has a set of methods that will be called in a particular order. Note that some of these methods are expected to return a specific value in order to progress to the next step.\n\n##### All Providers\n\n1. `options_pre(parser)`: Runs before option parsing. Use this method to add your own provider-specific command line arguments (See: [argparse](https://docs.python.org/3.6/library/argparse.html)).\n1. `options_post(parser, options)`: Runs after option parsing. Use this method to do things with your provider-specific command line arguments.\n\n##### Address Providers\n\n1. `fetch(options)`: Fetches and returns an IP address, hostname, etc.\n1. `validate(options, address)`: Returns `True` if the address is valid and `False` otherwise\n\n##### DNS Providers\n\n1. `check(options, address)`: Returns `True` if a DNS update is required and `False` otherwise\n1. `update(options, address)`: Returns `True` if a DNS update was successful and `False` otherwise\n\n#### Examples\n\nI'll write more documentation if people are interested, but for now, see the examples at [mcddns/provider](mcddns/provider) and [tests/provider](tests/provider).\n\n#### Releases\n\n1. Bump `version` in [pyproject.toml](pyproject.toml)\n1. Update [CHANGELOG.md](CHANGELOG.md)\n1. Run `make release`\n\n### To Do\n\n- Add tests for built-in providers\n",
    'author': 'Mike Conigliaro',
    'author_email': 'mike@conigliaro.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mconigliaro/mcddns',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
