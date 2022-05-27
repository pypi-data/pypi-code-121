# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pysnmp',
 'pysnmp.carrier',
 'pysnmp.carrier.asyncio',
 'pysnmp.carrier.asyncio.dgram',
 'pysnmp.carrier.asyncore',
 'pysnmp.carrier.asyncore.dgram',
 'pysnmp.carrier.asynsock',
 'pysnmp.carrier.asynsock.dgram',
 'pysnmp.entity',
 'pysnmp.entity.rfc3413',
 'pysnmp.entity.rfc3413.oneliner',
 'pysnmp.hlapi',
 'pysnmp.hlapi.asyncio',
 'pysnmp.hlapi.asyncore',
 'pysnmp.hlapi.asyncore.sync',
 'pysnmp.hlapi.asyncore.sync.compat',
 'pysnmp.proto',
 'pysnmp.proto.acmod',
 'pysnmp.proto.api',
 'pysnmp.proto.mpmod',
 'pysnmp.proto.proxy',
 'pysnmp.proto.secmod',
 'pysnmp.proto.secmod.eso',
 'pysnmp.proto.secmod.eso.priv',
 'pysnmp.proto.secmod.rfc3414',
 'pysnmp.proto.secmod.rfc3414.auth',
 'pysnmp.proto.secmod.rfc3414.priv',
 'pysnmp.proto.secmod.rfc3826',
 'pysnmp.proto.secmod.rfc3826.priv',
 'pysnmp.proto.secmod.rfc7860',
 'pysnmp.proto.secmod.rfc7860.auth',
 'pysnmp.smi',
 'pysnmp.smi.mibs',
 'pysnmp.smi.mibs.instances']

package_data = \
{'': ['*']}

install_requires = \
['pycryptodomex>=3.11.0,<4.0.0',
 'pysnmp-pyasn1>=1.0.3,<2.0.0',
 'pysnmp-pysmi>=1.0.4,<2.0.0']

setup_kwargs = {
    'name': 'pysnmplib',
    'version': '5.0.15',
    'description': '',
    'long_description': "\nSNMP library for Python\n-----------------------\n[![PyPI](https://img.shields.io/pypi/v/pysnmplib.svg?maxAge=2592000)](https://pypi.python.org/pypi/pysnmplib)\n[![Python Versions](https://img.shields.io/pypi/pyversions/pysnmplib.svg)](https://pypi.python.org/pypi/pysnmplib/)\n[![CI](https://github.com/pysnmp/pysnmp/actions/workflows/build-test-release.yml/badge.svg)](https://github.com/pysnmp/pysnmp/actions/workflows/build-test-release.yml)\n[![GitHub license](https://img.shields.io/badge/license-BSD-blue.svg)](https://raw.githubusercontent.com/pysnmp/pysnmp/master/LICENSE.rst)\n\nThis is a pure-Python, open source and free implementation of v1/v2c/v3\nSNMP engine distributed under 2-clause [BSD license](http://snmplabs.com/pysnmp/license.html).\n\nThe PySNMP project was initially sponsored by a [PSF](http://www.python.org/psf/) grant.\nThank you!\n\nFeatures\n--------\n\n* Complete SNMPv1/v2c and SNMPv3 support\n* SMI framework for resolving MIB information and implementing SMI\n  Managed Objects\n* Complete SNMP entity implementation\n* USM Extended Security Options support (3DES, 192/256-bit AES encryption)\n* Extensible network transports framework (UDP/IPv4, UDP/IPv6)\n* Asynchronous socket-based IO API support\n* [Asyncio](https://docs.python.org/3/library/asyncio.html) integration\n* [PySMI](http://snmplabs.com/pysmi/) integration for dynamic MIB compilation\n* Built-in instrumentation exposing protocol engine operations\n* Python eggs and py2exe friendly\n* 100% Python, works with Python 2.4 though 3.7\n* MT-safe (if SnmpEngine is thread-local)\n\nFeatures, specific to SNMPv3 model include:\n\n* USM authentication (MD5/SHA-1/SHA-2) and privacy (DES/AES) protocols (RFC3414, RFC7860)\n* View-based access control to use with any SNMP model (RFC3415)\n* Built-in SNMP proxy PDU converter for building multi-lingual\n  SNMP entities (RFC2576)\n* Remote SNMP engine configuration\n* Optional SNMP engine discovery\n* Shipped with standard SNMP applications (RC3413)\n\n\nDownload & Install\n------------------\n\nThe PySNMP software is freely available for download from [PyPI](https://pypi.python.org/pypi/pysnmplib)\nand [GitHub](https://github.com/pysnmp/pysnmp.git).\n\nJust run:\n\n```bash\n$ pip install pysnmp\n```\n    \nto download and install PySNMP along with its dependencies:\n\n* [PyASN1](http://snmplabs.com/pyasn1/)\n* [PyCryptodomex](https://pycryptodome.readthedocs.io) (required only if SNMPv3 encryption is in use)\n* [PySMI](http://snmplabs.com/pysmi/) (required for MIB services only)\n\nBesides the library, command-line [SNMP utilities](https://github.com/etingof/snmpclitools)\nwritten in pure-Python could be installed via:\n\n```bash\n$ pip install snmpclitools\n```\n    \nand used in the very similar manner as conventional Net-SNMP tools:\n\n```bash\n$ snmpget.py -v3 -l authPriv -u usr-md5-des -A authkey1 -X privkey1 demo.snmplabs.com sysDescr.0\nSNMPv2-MIB::sysDescr.0 = STRING: Linux zeus 4.8.6.5-smp #2 SMP Sun Nov 13 14:58:11 CDT 2016 i686\n```\n    \nExamples\n--------\n\nPySNMP is designed in a layered fashion. Top-level and easiest to use API is known as\n*hlapi*. Here's a quick example on how to SNMP GET:\n\n```python\nfrom pysnmp.hlapi import *\n\niterator = getCmd(SnmpEngine(),\n                  CommunityData('public'),\n                  UdpTransportTarget(('demo.snmplabs.com', 161)),\n                  ContextData(),\n                  ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))\n\nerrorIndication, errorStatus, errorIndex, varBinds = next(iterator)\n\nif errorIndication:  # SNMP engine errors\n    print(errorIndication)\nelse:\n    if errorStatus:  # SNMP agent errors\n        print('%s at %s' % (errorStatus.prettyPrint(), varBinds[int(errorIndex)-1] if errorIndex else '?'))\n    else:\n        for varBind in varBinds:  # SNMP response contents\n            print(' = '.join([x.prettyPrint() for x in varBind]))\n```\n\nThis is how to send SNMP TRAP:\n\n```python\nfrom pysnmp.hlapi import *\n\nerrorIndication, errorStatus, errorIndex, varBinds = next(\n    sendNotification(\n        SnmpEngine(OctetString(hexValue='8000000001020304')),\n        UsmUserData('usr-sha-aes128', 'authkey1', 'privkey1',\n                    authProtocol=usmHMACSHAAuthProtocol,\n                    privProtocol=usmAesCfb128Protocol),\n        UdpTransportTarget(('demo.snmplabs.com', 162)),\n        ContextData(),\n        'trap',\n        NotificationType(ObjectIdentity('SNMPv2-MIB', 'authenticationFailure'))\n    )\n)\n\nif errorIndication:\n    print(errorIndication)\n```\n\nWe maintain publicly available SNMP Agent and TRAP sink at \n[demo.snmplabs.com](http://snmplabs.com/snmpsim/public-snmp-agent-simulator.html). You are\nwelcome to use it while experimenting with whatever SNMP software you deal with.\n\n```bash\n$ python3 examples/hlapi/asyncore/sync/manager/cmdgen/usm-sha-aes128.py\nSNMPv2-MIB::sysDescr.0 = SunOS zeus.snmplabs.com 4.1.3_U1 1 sun4m\n$\n$ python3 examples//hlapi/asyncore/sync/agent/ntforg/v3-inform.py\nSNMPv2-MIB::sysUpTime.0 = 0\nSNMPv2-MIB::snmpTrapOID.0 = SNMPv2-MIB::warmStart\nSNMPv2-MIB::sysName.0 = system name\n```\n    \nOther than that, PySNMP is capable to automatically fetch and use required MIBs from HTTP, FTP sites\nor local directories. You could configure any MIB source available to you (including\n[this one](https://pysnmp.github.io/mibs/asn1/)) for that purpose.\n\nFor more example scripts please refer to [examples section](http://snmplabs.com/pysnmp/examples/contents.html#high-level-snmp)\nat pysnmp web site.\n\nDocumentation\n-------------\n\nLibrary documentation and examples can be found at the [pysnmp project site](http://snmplabs.com/pysnmp/).\n\nIf something does not work as expected, please\n[open an issue](https://github.com/etingof/pysnmp/issues) at GitHub or\npost your question [on Stack Overflow](http://stackoverflow.com/questions/ask) or try browsing pysnmp \n[mailing list archives](https://sourceforge.net/p/pysnmp/mailman/pysnmp-users/).\n\nBug reports and PRs are appreciated! ;-)\n\nCopyright (c) 2005-2019, [Ilya Etingof](mailto:etingof@gmail.com). All rights reserved.\n",
    'author': 'omrozowicz',
    'author_email': 'omrozowicz@splunk.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pysnmp/pysnmp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
