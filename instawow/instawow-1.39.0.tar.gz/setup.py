# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src',
 'instawow_gui': 'gui-webview/src/instawow_gui',
 'instawow_gui.frontend': 'gui-webview/src/instawow_gui/frontend',
 'instawow_gui.resources': 'gui-webview/src/instawow_gui/resources'}

packages = \
['instawow',
 'instawow.migrations',
 'instawow.migrations.versions',
 'instawow.wa_templates',
 'instawow_gui',
 'instawow_gui.frontend',
 'instawow_gui.resources']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4',
 'alembic>=1.7.0',
 'attrs>=21.4.0',
 'cattrs>=22.1.0',
 'click>=8.0.0',
 'exceptiongroup==1.0.0rc5',
 'iso8601>=1.0.2',
 'jinja2>=3.0.0',
 'loguru>=0.5.3',
 'pluggy>=0.13',
 'prompt-toolkit>=3.0.29,<4',
 'questionary>=1.10',
 'rapidfuzz>=1.4.1',
 'sqlalchemy>=1.4.23',
 'typing-extensions>=4.2.0',
 'yarl>=1.6.3']

extras_require = \
{'gui': ['aiohttp-rpc>=1.0.0', 'toga>=0.3.0.dev33'],
 'test': ['aresponses>=2.1.4',
          'coverage[toml]>=6.2',
          'pytest>=6.2.5',
          'pytest-asyncio>=0.17.0',
          'pytest-xdist>=2.5.0'],
 'types': ['sqlalchemy2-stubs']}

entry_points = \
{'console_scripts': ['instawow = instawow.cli:main']}

setup_kwargs = {
    'name': 'instawow',
    'version': '1.39.0',
    'description': 'World of Warcraft add-on manager',
    'long_description': "*instawow*\n==========\n\n.. image:: https://img.shields.io/matrix/wow-addon-management:matrix.org\n   :target: https://matrix.to/#/#wow-addon-management:matrix.org?via=matrix.org\n   :alt: Matrix channel\n\n*instawow* is an add-on manager for World of Warcraft.\nIt can be used to install, update and remove add-ons from GitHub,\nCurseForge, WoWInterface and Tukui.\n*instawow* has an interoperable CLI and GUI, fuzzy search with download scoring\nand several other goodies.\n\n.. list-table::\n   :widths: 50 50\n\n   * - .. figure:: https://asciinema.org/a/8m36ncAoyTmig4MXfQM8YjE6a.svg\n          :target: https://asciinema.org/a/8m36ncAoyTmig4MXfQM8YjE6a?autoplay=1\n          :alt: Asciicast demonstrating the operation of instawow\n          :width: 640\n     - .. figure:: https://raw.githubusercontent.com/layday/instawow/main/gui-webview/screenshots/v1.34.1.png\n          :target: https://github.com/layday/instawow/releases/latest\n          :alt: instawow-gui main window\n          :width: 640\n\nInstallation\n------------\n\nYou can download pre-built binaries of *instawow* from GitHub:\n\n- `Binaries <https://github.com/layday/instawow/releases/latest>`__\n\nIf you'd prefer to install *instawow* from source, you are able to choose from:\n\n- `pipx <https://github.com/pipxproject/pipx>`__:\n  ``pipx install instawow`` or ``pipx install instawow[gui]`` for the GUI\n- Vanilla pip:\n  ``python -m pip install -U instawow`` or ``python -m pip install -U instawow[gui]`` for the GUI\n\nCLI operation\n-------------\n\ntl;dr\n~~~~~\n\nBegin by running ``instawow reconcile``\nto register previously-installed add-ons with *instawow*\n(or ``instawow reconcile --auto`` to do the same without user input).\nTo install add-ons, you can search for them using the ``search`` command::\n\n    instawow search molinari\n\nIn addition, *instawow* is able to interpret add-on URLs and *instawow*-specific\nURNs of slugs and host IDs.\nAll of the following will install Molinari from CurseForge::\n\n    instawow install https://www.curseforge.com/wow/addons/molinari\n    instawow install curse:molinari\n    instawow install curse:20338\n\nYou can ``update`` add-ons and ``remove`` them just as you'd install them.\nIf ``update`` is invoked without arguments, it will update all of your\ninstalled add-ons.  You can ``list`` add-ons and view detailed information about\nthem using ``list --format detailed``.\nFor ``list`` and similarly non-destructive commands, the source can be omitted\nand the slug can be abbreviated, e.g. ``instawow reveal moli``\nwill open the Molinari add-on folder in your file manager.\n\nAdd-on reconciliation\n~~~~~~~~~~~~~~~~~~~~~\n\nAdd-on reconciliation is not automatic – *instawow* makes a point\nof not automatically assuming ownership of your add-ons.\nHowever, you can automate reconciliation with ``reconcile --auto``\nand *instawow* will prioritise add-ons from CurseForge.\nReconciled add-ons are reinstalled because the installed version cannot be\nextracted reliably.\n\nAdd-on search\n~~~~~~~~~~~~~\n\n*instawow* comes with a rudimentary ``search`` command\nwith results ranked based on edit distance and popularity.\nSearch uses a collated add-on catalogue which is updated\n`once daily <https://github.com/layday/instawow-data/tree/data>`__.\nYou can install multiple add-ons directly from search.\n\nReverting add-on updates\n~~~~~~~~~~~~~~~~~~~~~~~~\n\n*instawow* keeps a log of all versions of an add-on it has previously\ninstalled.\nAdd-on updates can be undone using the ``instawow rollback`` command.\nAdd-ons which have been rolled back are pinned and will not receive updates.\nRollbacks can themselves be undone with ``instawow rollback --undo``,\nwhich will install the latest version of the specified add-on using\nthe ``default`` strategy.\n\nProfiles\n~~~~~~~~\n\n*instawow* supports multiple game versions through the use of profiles.\nAssuming your default profile is configured for retail,\nyou can create a pristine profile for classic by running::\n\n    instawow -p classic configure\n\nYou can create profiles for other versions of the game (e.g. TBC, PTR or beta)\nin the same way.\nPrefix ``-p <profile>`` to *instawow* commands\nto manage each respective profile.\n\nThe ``any_flavour`` strategy can be used to install add-ons from CurseForge\nwhich do not have Classic releases but are known to work just as well::\n\n    instawow -p classic install -s any_flavour https://www.curseforge.com/wow/addons/colorpickerplus\n\nWeakAura updater\n~~~~~~~~~~~~~~~~\n\n*instawow* contains a WeakAura updater modelled after\n`WeakAuras Companion <https://weakauras.wtf/>`__.  To use the updater\nand provided that you have WeakAuras installed::\n\n    instawow weakauras-companion build\n    instawow install instawow:weakauras-companion\n\nYou will have to rebuild the companion add-on prior to updating\nto receive aura updates.  If you would like to check for updates on\nevery invocation of ``instawow update``, install the\n``instawow:weakauras-companion-autoupdate`` variant::\n\n    instawow install instawow:weakauras-companion-autoupdate\n    instawow update\n\nPlug-ins\n~~~~~~~~\n\n*instawow* can be extended using plug-ins.  Plug-ins can be used to add support\nfor arbitrary hosts and add new commands to the CLI.  You will find a sample\nplug-in in ``tests/plugin``.\n\nMetadata sourcing\n-----------------\n\nCurseForge\n~~~~~~~~~~\n\nCurseForge is set to retire its unauthenticated add-on API by the end of Q1 2022.\nCurseForge will be issuing keys for the new API conditionally and which\nadd-on managers are obligated to conceal.\nThe new API is therefore unworkable for add-on managers except through a\nproxy service, which the author of this particular add-on manager cannot afford.\nAt the same time, CurseForge will be providing the option for authors to unlist\ntheir add-ons from the new API, and downloads intitiated through the new API\nwill not count towards author credits for the ad revenue sharing programme.\n\nGitHub\n~~~~~~\n\n*instawow* supports WoW add-ons *released* on GitHub – that is to say that\nthe repository must have a release (tags won't work) and the release must\nhave an add-on ZIP file attached to it as an asset.\n*instawow* will not install or build add-ons directly from\nsource, or from tarballs or 'zipballs', and will not validate\nthe contents of the ZIP file.\n\nTransparency\n------------\n\nWeb requests initiated by *instawow* can be identified by its user agent string.\n\nEvery 24 hours, on launch, *instawow* will query `PyPI <https://pypi.org>`__ –\nthe canonical Python package index – to check for *instawow* updates.\n\nContributing\n------------\n\nBug reports and fixes are welcome.  Do open an issue before committing to\nmaking any significant changes.\n\nRelated work\n------------\n\nThe author of `strongbox <https://github.com/ogri-la/strongbox>`__ has been\ncataloguing similar software.  If you are unhappy\nwith *instawow*, you might find one of these\n`other <https://ogri-la.github.io/wow-addon-managers/>`__ add-on managers more\nto your liking.\n",
    'author': 'layday',
    'author_email': 'layday@protonmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
