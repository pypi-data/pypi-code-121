# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autonicer']

package_data = \
{'': ['*']}

install_requires = \
['astropy>4.2.1,<5.1',
 'astroquery>0.4.3',
 'numpy>1.20.3',
 'pandas>1.2.4',
 'termcolor>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['autonicer = autonicer:run']}

setup_kwargs = {
    'name': 'autonicer',
    'version': '1.0.2',
    'description': 'A program that retrieves NICER observational data sets and performs a default data reduction process on the NICER observational data',
    'long_description': "[![CI Tests](https://github.com/nkphysics/autoNICER/actions/workflows/ci.yaml/badge.svg?branch=master)](https://github.com/nkphysics/autoNICER/actions/workflows/ci.yaml)\n[![PyPI](https://img.shields.io/pypi/v/autonicer.svg)](https://pypi.org/project/autonicer/)\n# autoNICER\nA piece of software that allows for the automated retrieval, and default data reduction of NICER data. This software was developed to automate the retrieval of NICER data and perform standardized data reduction on the retrieved NICER data. \nThis project unaffiliated with the NICER team, NASA, the Goddard Space Flight Center (GSFC), and HEASARC. Thus, under no circumstances should anyone consider this project endorsed or recommended by the afformentioned agencies and organizations.\n\n## Contributing\nAnyone considering contribiting to this project is encouraged to do so.\nConstributing can be something as small as submitting issues you have found or requesting enhancements. Your feedback is incredibly valuable for improving the project.\nAll that is asked is that if you wish to contribute code please reach out in one way or another to nkphysics(Nick Space Cowboy), and submit a pull request.\nAnd if you want to see what's being worked on for future versions check out the open issues tagged as enhancements or the open projects under the projects tab.\n\nThank you. \n\n## Disclaimer\nThis software is licensed under the Apache 2.0 license, so it is free and open source for you to use.\nThis project unaffiliated with the NICER team, NASA, the Goddard Space Flight Center (GSFC), and HEASARC. Under no circumstances should anyone consider this project endorsed or recommended by the afformentioned agencies and organizations.\n\n## Pre-Requisite Software\n- HEASoft v6.29c, v6.30, RECOMMENDED v6.30.1 <https://heasarc.gsfc.nasa.gov/docs/software/lheasoft/>\n\nA video tutorial on how to generally install heasoft can be found here: <https://youtu.be/3-gobnSEuDo>\n- Remote CALDB <https://heasarc.gsfc.nasa.gov/docs/heasarc/caldb/caldb_remote_access.html>\n\nA video tutorial on how to setup Remote CALDB can be found here: <https://youtu.be/s01DF0cwOvM>\n- wget\n\n## Installation\n\nFor standard non-dev use cases (download the .whl or .tar.gz release)(https://github.com/nkphysics/autoNICER/releases/tag/v1.0.1) (normal pip installation coming soon maybe):\n\n\t$ pip3 install autonicer-1.0.1-py3-none-any.whl\n\nOR\n\n\t$ pip3 install autonicer-1.0.1.tar.gz\n\nFor development cases:\n- Clone the repo\n- cd into the project directory\n- make sure you are using poetry to help manage dependencies\n- Start working!\n\n## Basic Usage\n\n1. Initialize HEASoft.\n\n2. Go to the HEASARC archive in your web browser and query the NICERMASTER catalog for the source of your choice.\n\n2. Navigate to the desired directory where you want the NICER data that will be retrieved to be stored.\n\n3. Run autonicer by calling the local installation (i.e. `$ autonicer`)\n\t\n4. Upon starting autoNICER you will be asked to input the target source that you would like to query. Input the same source that you queryed in the web browser.\n\n5. Next you will be prompted to select the settings. You can select the following\n\t- If you want a barycenter correction performed\n\t- If a .csv log of the autoNICER run is written out\n\t- If the *ufa.evt files are compressed after reduction\n\n6. Next you will see the following prompt `autoNICER > `. Enter in the desired OBSID for the observation that you want retrieved and reduced. Better yet, copy the desired observation ID from the HEASARC archive and paste into the program. This will query that observation to be retrieved and processed. Type `sel` to see all the OBSID's you've selected. Type `cycle [cycle number]`(not with the brackets) to select all OBSID's from a specific cycle. You can use the `rm [all or OBSID]` or `back` commands to remove unwanted OBSID's that you may have selected by mistake. Type `done` when you have entered in all the observation IDs you want retrieved and reduced.\n\t\n7. You will see autoNICER start retrieving the data with wget, then that will be fed directly into `nicerl2`, then it will be barycenter corrected and lastly compressed in a .tar.gz format if you selected for it to happen. Selected OBSID's are retrieved and processed in series so autoNICER will move on the the next OBSID you've queryed up and give you back command of your terminal after it has retrieved and reduced all selected OBSIDs.\n",
    'author': 'Tsar Bomba Nick',
    'author_email': 'njkuechel@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
