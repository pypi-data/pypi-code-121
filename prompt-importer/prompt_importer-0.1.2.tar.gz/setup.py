# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['prompt_importer']

package_data = \
{'': ['*']}

install_requires = \
['beancount>=2.3.5,<3.0.0', 'blessed>=1.19.1,<2.0.0']

setup_kwargs = {
    'name': 'prompt-importer',
    'version': '0.1.2',
    'description': 'A base class for building prompt-based beancount importers',
    'long_description': '# Prompt Importer\n\nThis package provides a `PromptImporter` base class to build other beancount importers with.\nThe functionality `PromptImporter` provides is to prompt the user to input recipient accounts\nfor each transaction while keeping a list of common accounts for easy access.\nFor example:\n\n```\n02/05/2022: Online payment from CHK 1234, 100.00\nWhat should the recipient account be? (\'x\' to not extract a transaction)\n1. Expenses:Groceries   2. Expenses:Restaurants   3. Assets:Checking\n>>\n```\n\nIt also provides functionality to store regexes with which to automatically identify recipient accounts in the future.\n\n## Usage\n\n### Events\n\nTo create class that derives from `PromptImporter` you must first define a subclass of `prompt_importer.Event`.\nEvents represent single transactions from whatever type of file you are importing.\nFor example, if you are importing a `csv` file, you may have one event per row.\nThe subclass should implement the following methods:\n\n#### get_field(self, field: str) -> str\n\nEach event may have different fields associated with it.\nThis method should return the value of a field given an associated field name.\n\n#### get_id(self) -> str\n\nThis should return the **globally unique** id associated with an event.\n\n#### display(self) -> str\n\nThis is how the event will be displayed to the user before the prompt.\n\n#### get_transaction(self, filename: str, index: int, recipient_account: str) -> data.Transaction\n\nThis should return a transaction associated with an event.\nTo help build the transaction, it takes the file the event was sourced from, its index within the file, and the account that should be the "recipient" of the transaction.\n\nNote that the `data.Transaction` type refers to the `data` from `beancount.core`.\n\n### Importers\n\nOnce you have defined an event you can create a subclass of `PromptImporter`.\nTo do so, you must implement the typical methods associated with the beancount`importer.ImporterProtocol` class.\n**Important:** the value the method `name(self)` returns should _not_ contain characters not allowed in SQLite table names, such as periods.\n\nThe importer should also implement the following method:\n\n#### get_events(self, f) -> list[Event]\n\nGiven a beancount file this should return a list of events for the\nimporter to process.\n\n## Example\n\nThe following is an example of an event importer for Bank of America credit card reports. The implementation of the typical beancount importer methods (`identify`, `file`, etc.) are omitted as they are not the focus.\n\n```python\nimport csv\n\nfrom prompt_importer.importer import PromptImporter, Event\n\nfrom beancount.core import amount, data, flags\nfrom beancount.core.number import D\nfrom dateutil.parser import parse\n\nclass BofaCCEvent(Event):\n    def __init__(self, row):\n        self.data = {\n            "Posted Date": row["Posted Date"],\n            "Amount": row["Amount"],\n            "Payee": row["Payee"],\n            "Reference Number": row["Reference Number"],\n        }\n\n    def get_field(self, field: str) -> str:\n        return self.data[field]\n\n    def get_id(self) -> str:\n        return f"{self.data[\'Reference Number\']}"\n\n    def display(self) -> str:\n        return (\n            f"{self.data[\'Posted Date\']}: {self.data[\'Payee\']}, {self.data[\'Amount\']}"\n        )\n\n    def get_transaction(\n        self, filename: str, index: int, recipient_account: str\n    ) -> data.Transaction:\n        return data.Transaction(\n            meta=data.new_metadata(filename, index),\n            date=parse(self.data["Posted Date"]),\n            flag=flags.FLAG_OKAY,\n            payee=self.data["Payee"],\n            narration="",\n            tags=set(),\n            links=set(),\n            postings=[\n                data.Posting(\n                    "Liabilities:BofaCreditCard",\n                    amount.Amount(D(self.data["Amount"]), "USD"),\n                    None,\n                    None,\n                    None,\n                    None,\n                ),\n                data.Posting(recipient_account, None, None, None, None, None),\n            ],\n        )\n\n\nclass BofaCCImporter(PromptImporter):\n    def __init__(self, db_file):\n        super().__init__(db_file)\n\n    def name(self):\n        return "BofaCCImporter"\n\n    def get_events(self, f) -> list[Event]:\n        with open(f.name) as infile:\n            return [BofaCCEvent(row) for row in csv.DictReader(infile)]\n```\n',
    'author': 'Harry Eldridge',
    'author_email': 'eldridgemharry@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/heldridge/prompt_importer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
