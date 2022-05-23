# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['subscriber']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0', 'tenacity>=8.0.1,<9.0.0']

entry_points = \
{'console_scripts': ['podaac-data-downloader = '
                     'subscriber.podaac_data_downloader:main',
                     'podaac-data-subscriber = '
                     'subscriber.podaac_data_subscriber:main']}

setup_kwargs = {
    'name': 'podaac-data-subscriber',
    'version': '1.10.0',
    'description': 'PO.DAAC Data Subscriber Command Line Tool',
    'long_description': '[![Python Build](https://github.com/podaac/data-subscriber/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/podaac/data-subscriber/actions/workflows/python-app.yml)\n[![PyPi release](https://github.com/podaac/data-subscriber/actions/workflows/release.yml/badge.svg)](https://github.com/podaac/data-subscriber/actions/workflows/release.yml)\n\n\n# Scripted Access to PODAAC data\n\n ----\n\n![N|Solid](https://podaac.jpl.nasa.gov/sites/default/files/image/custom_thumbs/podaac_logo.png)\n\n\n## Subscriber or Bulk Download?\n\nThere are 2 tools in this repository, the data subscriber and the data downloader. Which you use depends on your use case. If you\'re not sure, we\'d recommend starting with the downloader.\n\n![Download or Subscribe?](/img/PO.DAAC%20Tools.png)\n\n**Downloader** - [Documentation](Downloader.md)\n\nThe Downloader is useful if you need to download PO.DAAC data once in a while or prefer to do it "on-demand". The subscriber makes no assumptions about the last time run or what is new in the archive, it simply uses the provided requests and downloads all matching data.\n\n**Subscriber** - [Documentation](Subscriber.md)\n\nThe subscriber is useful for users who need to continuously pull the latest data from the PO.DAAC archive. If you feed data into a model or real time process, the subscriber allows you to repeatedly run the script and only download the latest data.\n\n\n## Installation\n\nBoth subscriber and downloader require Python >= 3.7.\n\nThe subscriber and downloader scripts are available in the [pypi python repository](https://pypi.org/project/podaac-data-subscriber/), it can be installed via pip:\n\n```\npip install podaac-data-subscriber\n```\n\nyou should now have access to the downloader and subscriber Command line interfaces:\n\n```\n$> podaac-data-subscriber -h\nusage: podaac_data_subscriber.py [-h] -c COLLECTION -d OUTPUTDIRECTORY [-sd STARTDATE] [-ed ENDDATE] [-b BBOX] [-dc] [-dydoy] [-dymd] [-dy] [--offset OFFSET] [-m MINUTES]\n                                 [-e EXTENSIONS] [--process PROCESS_CMD] [--version] [--verbose] [-p PROVIDER]\n\n...\n```\n\n```\n$> podaac-data-downloader -h\nusage: PO.DAAC bulk-data downloader [-h] -c COLLECTION -d OUTPUTDIRECTORY [--cycle SEARCH_CYCLES] [-sd STARTDATE] [-ed ENDDATE] [-b BBOX] [-dc] [-dydoy] [-dymd] [-dy] [--offset OFFSET] [-e EXTENSIONS] [--process PROCESS_CMD] [--version] [--verbose] [-p PROVIDER] [--limit LIMIT]\n\n...\n```\n\n**Note:** If after installation, the `podaac-data-subscriber` or `podaac-data-downloader` commands are not available, you may need to add the script location to the PATH. This could be due to a *User Install* of the python package, which is common on shared systems where python packages are installed for the user (not the system). See [Installing to the User Site](https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-to-the-user-site) and [User Installs](https://pip.pypa.io/en/latest/user_guide/#user-installs) for more information on finding the location of installed scripts and adding them to the PATH.\n\n## Step 1:  Get Earthdata Login     \nThis step is needed only if you dont have an Earthdata login already.\nhttps://urs.earthdata.nasa.gov/\n> The Earthdata Login provides a single mechanism for user registration and profile  management for all EOSDIS system components (DAACs, Tools, Services). Your Earthdata login   also helps the EOSDIS program better understand the usage of EOSDIS services to improve  user experience through customization of tools and improvement of services. EOSDIS data are  openly available to all and free of charge except where governed by international  agreements.\n\nFor setting up your authentication, see the notes on the `netrc` file below.\n\n## Step 2: Setup your Earthdata Login\nThe netrc used within the script  will allow Python scripts to log into any Earthdata Login without being prompted for\ncredentials every time you run. The netrc file should be placed in your HOME directory.\nTo find the location of your HOME directory\n\nOn UNIX you can use\n```\necho $HOME\n```\nOn Windows you can use\n```\necho %HOMEDRIVE%%HOMEPATH%\n```\n\nThe output location from the command above should be the location of the `.netrc` (`_netrc` on Windows) file.\n\nThe format of the `netrc` file is as follows:\n\n```\nmachine urs.earthdata.nasa.gov\n    login <your username>\n    password <your password>\n```\nfor example:\n\n```\nmachine urs.earthdata.nasa.gov\n    login podaacUser\n    password podaacIsAwesome\n```\n\n**If the script cannot find the netrc file, you will be prompted to enter the username and password and the script wont be able to generate the CMR token**\n\n\n## Advanced Usage\n\n### Request data from another DAAC...\n\nUse the \'provider\' flag to point at a non-PO.DAAC provider. Be aware, the default data types (--extensions) may need to be specified if the desired data are not in the defaults.\n\n```\npodaac-data-subscriber -c SENTINEL-1A_SLC -d myData  -p ASF -sd 2014-06-01T00:46:02Z\n```\n\n### Logging\n\nFor error troubleshooting, one can set an environment variable to gain more insight into errors:\n\n```\nexport PODAAC_LOGLEVEL=DEBUG\n```\n\nAnd then run the script. This should give you more verbose output on URL requests to CMR, tokens, etc.\n\n\n### In need of Help?\nThe PO.DAAC User Services Office is the primary point of contact for answering your questions concerning data and information held by the PO.DAAC. User Services staff members are knowledgeable about both the data ordering system and the data products themselves. We answer questions about data, route requests to other DAACs, and direct questions we cannot answer to the appropriate information source.\n\nPlease contact us via email at podaac@podaac.jpl.nasa.gov\n',
    'author': 'PO.DAAC',
    'author_email': 'podaac@podaac.jpl.nasa.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/podaac/data-subscriber',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
