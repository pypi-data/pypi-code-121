# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scru128', 'scru128.cli']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['scru128 = scru128.cli:generate',
                     'scru128-inspect = scru128.cli:inspect']}

setup_kwargs = {
    'name': 'scru128',
    'version': '2.1.0',
    'description': 'SCRU128: Sortable, Clock and Random number-based Unique identifier',
    'long_description': '# SCRU128: Sortable, Clock and Random number-based Unique identifier\n\n[![PyPI](https://img.shields.io/pypi/v/scru128)](https://pypi.org/project/scru128/)\n[![License](https://img.shields.io/pypi/l/scru128)](https://github.com/scru128/python/blob/main/LICENSE)\n\nSCRU128 ID is yet another attempt to supersede [UUID] for the users who need\ndecentralized, globally unique time-ordered identifiers. SCRU128 is inspired by\n[ULID] and [KSUID] and has the following features:\n\n- 128-bit unsigned integer type\n- Sortable by generation time (as integer and as text)\n- 25-digit case-insensitive textual representation (Base36)\n- 48-bit millisecond Unix timestamp that ensures useful life until year 10889\n- Up to 281 trillion time-ordered but unpredictable unique IDs per millisecond\n- 80-bit three-layer randomness for global uniqueness\n\n```python\nfrom scru128 import scru128, scru128_string\n\n# generate a new identifier object\nx = scru128()\nprint(x)  # e.g. "036Z951MHJIKZIK2GSL81GR7L"\nprint(int(x))  # as a 128-bit unsigned integer\n\n# generate a textual representation directly\nprint(scru128_string())  # e.g. "036Z951MHZX67T63MQ9XE6Q0J"\n```\n\nSee [SCRU128 Specification] for details.\n\n[uuid]: https://en.wikipedia.org/wiki/Universally_unique_identifier\n[ulid]: https://github.com/ulid/spec\n[ksuid]: https://github.com/segmentio/ksuid\n[scru128 specification]: https://github.com/scru128/spec\n\n## Command-line interface\n\n`scru128` generates SCRU128 IDs.\n\n```bash\n$ scru128\n036ZG4ZLMDWDZ8414EIM77VCT\n$ scru128 -n 4\n036ZG4ZLV707WNCZL108KY4I7\n036ZG4ZLV707WNCZL12TOWMHO\n036ZG4ZLV707WNCZL14HIRM6N\n036ZG4ZLV707WNCZL17110SHH\n```\n\n`scru128-inspect` prints the components of given SCRU128 IDs as human- and\nmachine-readable JSON objects.\n\n```bash\n$ scru128 -n 2 | scru128-inspect\n{\n  "input":        "036ZG552N91MT9S0GYHDWIF95",\n  "canonical":    "036ZG552N91MT9S0GYHDWIF95",\n  "timestampIso": "2022-03-20T08:34:01.493+00:00",\n  "timestamp":    "1647765241493",\n  "counterHi":    "10145723",\n  "counterLo":    "13179084",\n  "entropy":      "4167049657",\n  "fieldsHex":    ["017fa6763e95", "9acfbb", "c918cc", "f86021b9"]\n}\n{\n  "input":        "036ZG552N91MT9S0GYJ7I56SJ",\n  "canonical":    "036ZG552N91MT9S0GYJ7I56SJ",\n  "timestampIso": "2022-03-20T08:34:01.493+00:00",\n  "timestamp":    "1647765241493",\n  "counterHi":    "10145723",\n  "counterLo":    "13179085",\n  "entropy":      "3838717859",\n  "fieldsHex":    ["017fa6763e95", "9acfbb", "c918cd", "e4ce2fa3"]\n}\n```\n\n## License\n\nLicensed under the Apache License, Version 2.0.\n',
    'author': 'LiosK',
    'author_email': 'contact@mail.liosk.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/scru128/python',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
