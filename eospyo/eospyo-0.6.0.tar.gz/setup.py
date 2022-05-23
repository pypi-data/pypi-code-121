# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eospyo', 'eospyo.contracts']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.22', 'pydantic>=1.9.0,<2.0.0', 'ueosio>=0.2.6,<0.3.0']

setup_kwargs = {
    'name': 'eospyo',
    'version': '0.6.0',
    'description': 'Interact with EOSIO blockchain networks',
    'long_description': 'Minimalist python library to interact with eosio blockchain networks\n\n\n# What is it?\n**eospyo** is a python library to interact with EOSIO blockchains.  \nIts main focus are server side applications.  \nThis library is heavily influenced (and still uses some pieces of code from) by [µEOSIO](https://github.com/EOSArgentina/ueosio). Many thanks to them for the astonishing job!  \n\n\n# Main features\n- <ins>Send transactions</ins>  \nIts main usage today is to send transactions to the blockchain\n- <ins>Statically typed</ins>  \nThis library enforces and verifies types and values.\n- <ins>Serialization</ins>  \n**eospyo** serializes the transaction before sending to the blockchain. \n- <ins>Paralellization</ins>  \nAlthough python has the [GIL](https://realpython.com/python-gil/) we try to make as easier as possible to paralellize the jobs.  \nAll data is as immutable and all functions are as pure as we can make them.  \n\n\n# Stability\nThis work is in alpha version. That means that we make constant breaking changes to its api.  \nAlso there are known (and, of course unknown) bugs and various limitations.  \nGiven that, we at [FACINGS](https://facings.io/) have been using this library in production for some few months now.  \nHowever we\'d advise for you to fix its version when deploying to prod.  \n\n\n# Using\nJust `pip install eospyo` and play around.  \n(we don\'t support, and have no plans to support [conda](https://docs.conda.io/en/latest/))  \nRather then starting with long docs, just a simple example:  \n\n\n## Use Send Message action\n```\nimport eospyo\n\n\nprint("Create Transaction")\ndata=[\n    eospyo.Data(\n        name="from",\n        value=eospyo.types.Name("me.wam"), \n    ),\n    eospyo.Data(\n        name="message",\n         value=eospyo.types.String("hello from eospyo"),\n    ),\n]\n\nauth = eospyo.Authorization(actor="me.wam", permission="active")\n\naction = eospyo.Action(\n    account="me.wam", # this is the contract account\n    name="sendmsg", # this is the action name\n    data=data,\n    authorization=[auth],\n)\n\nraw_transaction = eospyo.Transaction(actions=[action])\n\nprint("Link transaction to the network")\nnet = eospyo.WaxTestnet()  # this is an alias for a testnet node\n# notice that eospyo returns a new object instead of change in place\nlinked_transaction = raw_transaction.link(net=net)\n\n\nprint("Sign transaction")\nkey = "a_very_secret_key"\nsigned_transaction = linked_transaction.sign(key=key)\n\n\nprint("Send")\nresp = signed_transaction.send()\n\nprint("Printing the response")\nresp_fmt = json.dumps(resp, indent=4)\nprint(f"Response:\\n{resp_fmt}")\n```\n\nThere are some other examples [here](./examples)\n\n\n# Known bugs\n### Keys not working\n- Some keys are reported to not work. However this error was not replicated and the cause remains unknown. If you can share a key pair that is not working it would be very helpful.\n### multi-byte utf-8 characters can not be serialized\n- Serialization of multi-byte utf-8 characters is somewhat unpredictable in the current implementation, therfore any String input containing multi-utf8 byte characters will be blocked for the time being.\n\n\n# Contributing\nAll contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.  \nIf you find a bug, just open a issue with a tag "BUG".  \nIf you want to request a new feature, open an issue with a tag "ENH" (for enhancement).  \nIf you feel like that our docs could be better, please open one with a tag "DOC".  \nAlthough we have the next few steps already planned, we are happy to receive the community feedback to see where to go from there.  \n\n\n### Development\nIf you want to develop for **eospyo**, here are some tips for a local development environment.\nWe\'ll be more then happy to receive PRs from the community.\nAlso we\'re going full [Black](https://black.readthedocs.io/en/stable/) and enforcing [pydocstyle](http://www.pydocstyle.org/en/stable/) and [isort](https://pypi.org/project/isort/) (with the limitations described in the .flake8 file)\n\n#### Setup\nCreate a virtual env\nEnsure the dependencies are met:\n```\npip install poetry\npoetry install\n```\n\n#### Run tests\nThe tests are run against a local network.  \nBefore running the tests you\'ll need to `docker-compose up` to create the local network, users and contracts used in the tests.  \nWhen ready, just:\n```\npytest\n```\n\n\n\n',
    'author': 'Edson',
    'author_email': 'eospyo@facings.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/FACINGS/eospyo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
