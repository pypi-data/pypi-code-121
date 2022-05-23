# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spicypy', 'spicypy.control', 'spicypy.signal']

package_data = \
{'': ['*']}

install_requires = \
['astropy>=3.0',
 'control>=0.8.1,<1.0',
 'gwpy>=2.0.4,<3.0',
 'h5py>=3,<4',
 'lpsd>=0.2,<0.3',
 'matplotlib>=3.0,<4.0',
 'numpy>=1.18,<2.0',
 'scipy>=1.5,<2.0']

setup_kwargs = {
    'name': 'spicypy',
    'version': '0.2.1',
    'description': 'A python package for signal processing & control systems. Combining several tools to facilitate signal processing, control systems modelling, and the interface between the two.',
    'long_description': '# spicypy\n\nSignal processing & control systems. Combining several tools to facilitate signal processing, control systems modelling,\nand the interface between the two.\n\n[Documentation](https://pyda-group.gitlab.io/spicypy/)\n\n# Development roadmap\n\nWe are currently working on software requirements [specification](https://gitlab.com/pyda-group/spicipy/-/wikis/home/specification).\nSee also [meetings](https://gitlab.com/pyda-group/spicypy/-/wikis/home/meetings) and\n[Issues](https://gitlab.com/pyda-group/spicypy/-/issues) for more information.\n\nThe project is open for contributions, and feedback on usage is welcome. For reporting bugs and specific code suggestions\nplease consider [creating an Issue](https://gitlab.com/pyda-group/spicypy/-/issues/new?issue%5Bmilestone_id%5D=).\nFor other enquiries contact details are provided below.\n\n# Contact\n\n* Artem Basalaev (artem.basalaevATphysikDOTuni-hamburg.de)\n* Christian Darsow-Fromm (cdarsowfATphysnetDOTuni-hamburg.de)\n* Martin Hewitson (martin.hewitsonATaeiDOTmpg.de)\n* Oliver Gerberding (oliver.gerberdingATphysikDOTuni-hamburg.de)\n\n\n# License\n\nLicensed under the Apache License, Version 2.0 (the "License");\nyou may not use this file except in compliance with the License.\nYou may obtain a copy of the License at\n\n[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)\n\n  Unless required by applicable law or agreed to in writing, software\n  distributed under the License is distributed on an "AS IS" BASIS,\n  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n  See the License for the specific language governing permissions and\n  limitations under the License.\n',
    'author': 'Artem Basalaev',
    'author_email': 'artem.basalaev@physikDOTuni-hamburg.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/pyda-group/spicypy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
