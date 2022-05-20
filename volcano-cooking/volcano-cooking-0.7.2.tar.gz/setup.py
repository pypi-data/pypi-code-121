# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['volcano_cooking',
 'volcano_cooking.configurations',
 'volcano_cooking.helper_scripts',
 'volcano_cooking.modules.convert',
 'volcano_cooking.modules.create',
 'volcano_cooking.plotting']

package_data = \
{'': ['*']}

install_requires = \
['PyWavelets>=1.1.1,<2.0.0',
 'cftime>=1.5.0,<2.0.0',
 'click>=8.0.1,<9.0.0',
 'cosmoplots>=0.1.5,<0.2.0',
 'dask>=2022.3.0,<2023.0.0',
 'matplotlib>=3.4.2,<4.0.0',
 'netCDF4>=1.5.8,<2.0.0',
 'numpy>=1.21.1,<2.0.0',
 'scipy>=1.7.1,<2.0.0',
 'superposed-pulses>=1.2,<2.0',
 'wget>=3.2,<4.0',
 'xarray>=0.21.1,<0.22.0']

entry_points = \
{'console_scripts': ['sfrc-sparse2lin = volcano_cooking.sparse_to_lin:main',
                     'view-frc = volcano_cooking.view_force:main',
                     'volcano-cooking = volcano_cooking.__main__:main']}

setup_kwargs = {
    'name': 'volcano-cooking',
    'version': '0.7.2',
    'description': 'Make some volcanoes and simulate them in CESM2',
    'long_description': "# Volcano Cooking\n\n[![codecov](https://codecov.io/gh/engeir/volcano-cooking/branch/main/graph/badge.svg?token=8I5VE7LYA4)](https://codecov.io/gh/engeir/volcano-cooking)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n> Let's make some volcanoes erupt!\n\n__NOTE:__\nThe created dates *must* start before the model start. Running CESM2 from year 1850 with\nthe first eruption in 1850 will make it crash. Setting the first eruption to 1849,\nhowever, will make it run. The same goes for the end, the model must stop prior to the\nlast event, otherwise it will crash. This project will make sure one event is placed\nahead of the `init` year, but the end will vary depending on number of events created\nand their frequency.\n\n## Install\n\nThis repo is currently intended to be installed from source only. To install all\ndependencies, clone the repo and install with [poetry](https://python-poetry.org):\n\n```sh\ngit clone https://github.com/engeir/volcano-cooking.git\ncd volcano-cooking\npoetry install\n# or, without development dependencies:\npoetry install --no-dev\n```\n\n## Usage\n\nThere are two CLI programs coming with this project. The main program is\n`volcano-cooking`, which will create a `.nc` and `.npz` file in the `data/output`\ndirectory. With the `view_frc` program you can quickly view the content of the created\nfiles in a plot.\n\nRun from within this repository/directory via poetry:\n\n```sh\npoetry run volcano-cooking\npoetry run view-frc <file.nc>\n```\n\nor, if the virtual environment where the project is installed is activated:\n\n```sh\nvolcano-cooking\nview-frc <file.nc>\n```\n\nAn optional flag can be sent to the `view-frc` program that will save the plot:\n`view-frc -s <file.nc>`.\n\nIn either case a `data/output` directory will be created inside the current directory\nwhen something is saved.\n\nFor more options to either `volcano-cooking` or `view-frc`, see\n\n```sh\nvolcano-cooking --help\nview-frc --help\n```\n\n### Option 0 (default, using NCL-script)\n\n#### TL;DR\n\n```console\n$ volcano-cooking -f 1 -s 100\nGenerating with 'GenerateFPP'...\n$ sh _script/create_cesm_frc.sh\n Copyright (C) 1995-2019 - All Rights Reserved\n University Corporation for Atmospheric Research\n NCAR Command Language Version 6.6.2\n The use of this software is governed by a License Agreement.\n See http://www.ncl.ucar.edu/ for more details.\n(0)     in data/originals/createVolcEruptV3.ncl\n...\n  long_name :   SO2 elevated emissions from explosive volcanoes\n  _FillValue :  9.96921e+36\n(0)     saving stratvolc\n(0)     File creation complete: data/cesm/VolcanEESMv3.11Enger_SO2_850-2016_Mscale_Zreduc_2deg_c20220502-140023.nc\nLog file created at data/cesm/logs/20220502-140022.log\nFixing the attributes of the altitude_int coordinate...\n$ sh _script/package_last.sh\nSuccessfully placed all latest source files in the 'source-files' directory.\n$ ls source-files\n20220502-140022.log                     VolcanEESMv3.11Enger_SO2_850-2016_Mscale_Zreduc_2deg_c20220502-140023.nc\nsynthetic_volcanoes_20220502_135956.nc  synthetic_volcanoes_20220502_135956.npz\n```\n\n#### Dependencies\n\nThis option needs\n\n- `volcano-cooking` installed\n- A coordinate file (~ 10 kB)\n- [`ncl`](https://www.ncl.ucar.edu/Download/) executable\n\n#### Create source file for forcing\n\nRun command `volcano-cooking` with the options you want. See `volcano-cooking --help`.\n\n#### Create forcing file for CESM2\n\n> Running the [_script/create_cesm_frc.sh](_script/create_cesm_frc.sh) script depends on\n> having `ncl` installed. See installation instructions\n> [here](https://www.ncl.ucar.edu/Download/).\n\nAfter having run the `volcano-cooking` command, the forcing file for CESM2 can be\ngenerated by running\n\n```sh\nsh _script/create_cesm_frc.sh\n```\n\nIf the needed coordinate files are missing, you will be asked if you want to download\nthem. If you want to use different files, or change the default resolution (default is\n2 degrees), edit [_script/create_cesm_frc.sh](_script/create_cesm_frc.sh) accordingly.\nIn this case, you also need to manually download whatever coordinate file you want to\nuse. See section [Setting up manually](#setting-up-manually).\n\n#### Wrap up\n\nThe last created files, source files, logs and final output, can be nicely collected and\nplaced in a directory named `source-files` with command:\n\n```sh\nsh _script/package_last.sh\n```\n\n<details><summary><h4>Setting up manually</h4></summary><br>\n\nTo be able to create forcing files used by CESM2 from the newly created synthetic file,\nwe need a script from the [emissions][data_source_files] directory. These are scripts\nthat use the forcing file this project generates to make a new, full forcing file that\nCESM2 accepts (examples of such files can be found [here][volc-frc-complete]). For\nexample, `createVolcEruptV3.ncl` can be found in the [emissions][data_source_files]\ndirectory. This need a `common.ncl` file, found [here][common-ncl], in addition to other\nstandard `ncl` libraries. Make sure to edit `createVolcEruptV3.ncl` to read the created\nfile and that the first and last year cover those used in the created file. A working\nversion of `createVolcEruptV3.ncl` that uses input files generated by `volcano-cooking`\ncan be found in [data/originals](data/originals). To see what was changed from the\noriginal, run `diff createVolcEruptV3.ncl createVolcEruptV3.ncl.original`.\n\nCoordinate files are needed when running `createVolcEruptV3.ncl` or similar scripts, and\nare located [here][coord-file]. For example `fv_1.9x2.5_L30.nc` which can be used with\ntwo degrees resolution in the atmosphere model. The following commands will download\n1 and 2 degree resolution coordinate files, respectively, to the `data/originals`\ndirectory:\n\n```sh\nwget --no-check-certificate https://svn-ccsm-inputdata.cgd.ucar.edu/trunk/inputdata/atm/cam/coords/fv_0.9x1.25_L30.nc --directory-prefix data/originals\nwget --no-check-certificate https://svn-ccsm-inputdata.cgd.ucar.edu/trunk/inputdata/atm/cam/coords/fv_1.9x2.5_L30.nc --directory-prefix data/originals\n```\n\n</details>\n\n### Option 1 (directly change forcing file)\n\n#### TL;DR\n\n```console\n$ volcano-cooking -f 1 -s 100 -o\nGenerating with 'GenerateFPP'...\n```\n\n#### Dependencies\n\nThis option needs\n\n- `volcano-cooking` installed\n- A coordinate file (~ 10 kB)\n- Original CESM2 forcing file (~ 2.2 GB)\n\n#### Run library\n\nNow the only thing we need to do is running `volcano-cooking` with the flag `-o`, and\nchoose the type of forcing we want (see `volcano-cooking --lst`):\n\n```sh\nvolcano-cooking -f 1 -s 100 -o\n```\n\n<details><summary><h4>Get forcing and coordinate files manually</h4></summary><br>\n\n> Manually downloading the files and placing them in the correct directory is *not*\n> needed. Running the command as shown above will ask you if you want to download the\n> files, and place them where they need to be.\n\nThis option relies on having a working forcing file and coordinate file at hand. We will\nuse the forcing file that CESM2 places in the `stratvolc` directory of the `cam` model.\nDownload from [this link][stratvolc-forcing] and place it in the `data/originals`\ndirectory, or run command:\n\n```sh\nwget --no-check-certificate https://svn-ccsm-inputdata.cgd.ucar.edu/trunk/inputdata/atm/cam/chem/stratvolc/VolcanEESMv3.11_SO2_850-2016_Mscale_Zreduc_2deg_c191125.nc --directory-prefix data/originals\n```\n\nIt's 2.2\xa0GB file, so it will take some time.\n\nWe will also need a coordinate file, specifically `fv_1.9x2.5_L30.nc` which is found\n[here][coord-file]. This file is small and quick to download. From the command line:\n\n```sh\nwget --no-check-certificate https://svn-ccsm-inputdata.cgd.ucar.edu/trunk/inputdata/atm/cam/coords/fv_0.9x1.25_L30.nc --directory-prefix data/originals\nwget --no-check-certificate https://svn-ccsm-inputdata.cgd.ucar.edu/trunk/inputdata/atm/cam/coords/fv_1.9x2.5_L30.nc --directory-prefix data/originals\n```\n\n</details>\n\n## Extra\n\n### Compare created file with a similar used in a default CESM2 experiment\n\nA similar file to those that are created is needed to be able to use some scripts in the\n`helper_scripts` directory. By default, it assumes the file is named\n`volcan-eesm_global_2015_so2-emissions-database_v1.0.nc` and that it is placed inside\nthe `data/originals` directory. You can find this file [here][volc-frc].\n\n## TODO\n\n- [ ] Simplify process of creating new forcing generator classes\n\n[data_source_files]: https://svn.code.sf.net/p/codescripts/code/trunk/ncl/emission\n[common-ncl]: http://svn.code.sf.net/p/codescripts/code/trunk/ncl/lib/common.ncl\n[coord-file]: https://svn-ccsm-inputdata.cgd.ucar.edu/trunk/inputdata/atm/cam/coords/\n[coords-repo]: https://svn-ccsm-inputdata.cgd.ucar.edu/trunk/inputdata/share/scripgrids/\n[volc-frc]: http://catalogue.ceda.ac.uk/uuid/bfbd5ec825fa422f9a858b14ae7b2a0d\n[volc-frc-complete]: https://svn-ccsm-inputdata.cgd.ucar.edu/trunk/inputdata/atm/cam/chem/stratvolc/\n[stratvolc-forcing]: https://svn-ccsm-inputdata.cgd.ucar.edu/trunk/inputdata/atm/cam/chem/stratvolc/VolcanEESMv3.11_SO2_850-2016_Mscale_Zreduc_2deg_c191125.nc\n",
    'author': 'engeir',
    'author_email': 'eirroleng@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
