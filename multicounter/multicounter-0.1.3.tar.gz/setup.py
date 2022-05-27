# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['multicounter']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'multicounter',
    'version': '0.1.3',
    'description': 'A simple, elegant counter with support for counting multiple things at once.',
    'long_description': "<!--\n Copyright (c) 2022 Joseph Hale\n\n This Source Code Form is subject to the terms of the Mozilla Public\n License, v. 2.0. If a copy of the MPL was not distributed with this\n file, You can obtain one at http://mozilla.org/MPL/2.0/.\n-->\n\n# MultiCounter\n\nA simple, elegant counter with support for counting multiple things at once.\n\n## Installation\n\n### Pip\n```bash\npip install multicounter\n```\n\n### Poetry\n```bash\npoetry add multicounter\n```\n\n## Usage\n```python\nfrom multicounter import MultiCounter\nmc = MultiCounter()\n\n# Choose a name for your counter and start counting!\nmc.foo += 1\n\n# You can choose an initial value for a counter ...\nmc.bar = 42\n# ... and increment or decrement it however you like.\nmc.bar -= 4\n\nprint(mc.get_counters())\n# {'foo': 1, 'bar': 38}\n```\n\n## Contributing\nSee [CONTRIBUTING.md](CONTRIBUTING.md)\n\n## The Legal Stuff\n\n```\n`MultiCounter` by Joseph Hale is licensed under the terms of the Mozilla\nPublic License, v 2.0, which are available at https://mozilla.org/MPL/2.0/.\n\nYou can download the source code for `MultiCounter` for free from\nhttps://github.com/jhale1805/multicounter.\n```\n\n### TL;DR\n\nYou can use files from this project in both open source and proprietary\napplications, provided you include the above attribution. However, if\nyou modify any code in this project, or copy blocks of it into your own\ncode, you must publicly share the resulting files (note, not your whole\nprogram) under the MPL-2.0. The best way to do this is via a Pull\nRequest back into this project.\n\nIf you have any other questions, you may also find Mozilla's [official\nFAQ](https://www.mozilla.org/en-US/MPL/2.0/FAQ/) for the MPL-2.0\nlicense insightful.\n\nIf you dislike this license, you can contact me about negotiating a\npaid contract with different terms.\n\n**Disclaimer:** This TL;DR is just a summary. All legal questions\nregarding usage of this project must be handled according to the\nofficial terms specified in the `LICENSE` file.\n\n### Why the MPL-2.0 license?\n\nI believe that an open-source software license should ensure that code\ncan be used everywhere.\n\nStrict copyleft licenses, like the GPL family of licenses, fail to\nfulfill that vision because they only permit code to be used in other\nGPL-licensed projects. Permissive licenses, like the MIT and Apache\nlicenses, allow code to be used everywhere but fail to prevent\nproprietary or GPL-licensed projects from limiting access to any\nimprovements they make.\n\nIn contrast, the MPL-2.0 license allows code to be used in any software\nproject, while ensuring that any improvements remain available for\neveryone.\n",
    'author': 'Joseph Hale',
    'author_email': 'me@jhale.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jhale1805/multicounter',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
