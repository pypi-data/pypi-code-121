# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tc2100']

package_data = \
{'': ['*']}

install_requires = \
['pyserial>=3.4,<4.0', 'twisted>=22.1,<23.0']

extras_require = \
{'docs': ['sphinx>=1.6.7,<1.7.0',
          'sphinx_rtd_theme>=1.0.0,<1.1.0',
          'm2r2>=0.3.2,<0.4.0']}

entry_points = \
{'console_scripts': ['tc2100dump = tc2100.__main__:main']}

setup_kwargs = {
    'name': 'tc2100',
    'version': '0.1.5',
    'description': 'Receive data from a compatible USB digital thermometer',
    'long_description': '# TC2100 Thermometer Interface\n\n> Receive measurements from your TC2100 or other compatible digital thermometer\n> over USB.\n\n## Motivation\n\nThe TC2100 is a digital thermometer which supports\n\n* two simultaneous measurement channels; and\n* seven standard types of thermocouples.\n\nAlthough it is usable as a standalone meter, it also includes a USB interface\nfor real-time computer output.\n\nThe manufacturer provides software for the USB interface. *This is not it.*\nThis is unsupported, third-party software which was developed by reverse\nengineering.\n\nThe `tc2100` module is a python\xa03.9 software development kit for receiving\nreal-time temperature measurements. It includes a console script, `tc2100dump`,\nfor logging measurements to [csv](https://docs.python.org/3.6/library/csv.html)\nfiles.\n\n## Supported Devices\n\nAt present, only one device is supported by this module.\n\n| Name                   | Vendor ID (hex)  | Product ID (hex)  |\n|------------------------|------------------|-------------------|\n| TC2100                 | `10c4`           | `ea60`            |\n\nOther devices have not been tested and are unlikely to work. If you have another\ndevice which works, open a bug report and ask that it be added to this table.\n\n## The Fine Print\n\nIn case you missed it above, this project is not affiliated with the original\nmanufacturer(s). To our knowledge, the telemetry format is not specified in any\n[other] public documents. It has been reverse-engineered without assistance or\nsupport from the manufacturer. Read the\n[license](https://github.com/cbs228/tc2100/blob/master/LICENSE) carefully, as\nit may affect your rights. There is no warranty.\n\n*Use of these programs in safety-critical applications is strongly discouraged.*\n\n## Installation\n\n```bash\npip3 install tc2100\n```\n\nThis module requires [twisted](http://twistedmatrix.com/) and\n[pyserial](https://pyserial.readthedocs.io/en/latest/pyserial.html). The pip\npackage will automatically install these dependencies.\n\n## Quick Start\n\nUsing the supplied USB cable, connect a TC2100 thermometer to your computer.\nHold down the "`PC-Link`" button until the meter beeps and the "`USB`" indicator\nilluminates. Then run:\n\n```bash\ntc2100dump --out temperatures.csv\n```\n\nIf you receive "`permission denied`" errors on Linux, you need to grant your\nuser account permission to use serial devices. On most distributions, including\nUbuntu and CentOS, this can be accomplished by adding yourself to the `dialout`\ngroup:\n\n```bash\nsudo usermod -a -G dialout "$USER"\n```\n\nOnce you perform the above modification, you will need to log out and log back\nin again. Never run this program as root!\n\nWhen running `tc2100dump`, you may omit the `--out` argument to write\nmeasurements to standard output. You may also call this module as an executable\nwith\n\n```bash\npython3 -m tc2100 --out temperatures.csv\n```\n\nThe script will attempt to auto-detect the correct port for your thermometer.\nIf auto-detection fails, you may specify the port manually:\n\n```bash\ntc2100dump --port /dev/ttyUSB0 --out temperatures.csv\n```\n\nIf the script detects your thermometer, but no data is printed, check to make\nsure you have pressed the "`PC-Link`" button and that the "`USB`" indicator\nis illuminated.\n\n## Development Status\n\nThis module is likely *feature-complete*. It does what I need it to do, and\nadditional features are not planned. Bug reports which are broadly categorized\nas feature requests will probably be rejected. I am also unable to support the\ninclusion of additional devices—even similar ones.\n\nIf you observe inconsistencies or other issues with the telemetry output, and\ncan identify them, please submit a bug report. If able, please include a capture\nof the serial data stream and the expected behavior with your report.\n\nPull requests within the scope of this project are welcome, especially if they\nfix bugs. Please ensure that your PRs include tests and pass the included `tox`\nchecks.\n\n## Technical Details\n\nThe TC2100 incorporates a UART-to-USB chipset, which emulates a serial port over\nUSB. When plugged in, most computers will automatically detect it as a serial\nport, like `/dev/ttyUSB0` or `COM1`. No additional drivers are required.\n\nThe thermometer has a USB vendor\xa0ID of `0x10c4` and a product\xa0ID of `0xea60`.\nThe meter\'s serial adapter uses `9600`\xa0baud with the common `8N1`\xa0format: eight\ndata bits, no parity, and one stop bit.\n\nOnce the "PC Link" button is pressed, updates begin to stream immediately, at\nregular intervals. Each update is an 18\xa0byte packet which begins with the hex\nbytes `b"\\x65\\x14"` and ends with a CRLF (`b"\\x0d\\x0a"`). Multi-byte quantities\nare sent `big endian`.\n\nThis is an example update, in hex:\n\n```\n65 14 00 00 00 00 8D 09 0C 01 81 88 40 00 02 05 0D 0A\n```\n\nBytes are decoded as follows:\n\n| Offset (dec)  | C Type        | Description                     |\n|---------------|---------------|---------------------------------|\n| 0             | `uint8[2]`    | Header                          |\n| 2             | `uint8[3]`    | Unknown—always zeros            |\n| 5             | `int16`       | Channel 1 measurement           |\n| 7             | `int16`       | Channel 2 measurement           |\n| 9             | `uint8`       | Thermocouple type, other data   |\n| 10            | `uint8`       | Display unit, other data        |\n| 11            | `uint8`       | Channel 1 flags                 |\n| 12            | `uint8`       | Channel 2 flags                 |\n| 13            | `uint8`       | Hours                           |\n| 14            | `uint8`       | Minutes                         |\n| 15            | `uint8`       | Seconds                         |\n| 16            | `uint8[2]`    | CRLF                            |\n\n* The update message cannot be expressed as a C\xa0struct, as it lacks the proper\n  alignment.\n* Measurement **values** are\n  - expressed in tenths of degrees\n  - in sign-magnitude format. The sign bit is part of the flag bytes (11 and 12)\n  - expressed in the same units as the thermometer is set to display. Byte 10\n    indicates the unit of measure.\n* Channel **flags** are OR\'d together:\n  - Valid measurement: `0x08`\n  - Invalid measurement: `0x40`. Channels which do not have a thermocouple\n    connected will have this flag.\n  - Negative measurement: `0x80`\n* The thermocouple **type** and temperature **units** are stored in the least\n  significant nibble of those bytes. The upper nibble contains other data.\n\nThe above measurement is in degrees Celsius. The channel\xa01 measurement is\n`-14.1 °C`, and the channel\xa02 measurement is invalid.\n\nFurther details are included in the python class `tc2100.Observation`. Unit\ntests include more sample data.\n\n----\n\nLicense - [MIT](https://github.com/cbs228/tc2100/blob/master/LICENSE)\n',
    'author': 'Colin S.',
    'author_email': '3526918+cbs228@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
