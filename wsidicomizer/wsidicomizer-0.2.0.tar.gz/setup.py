# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wsidicomizer']

package_data = \
{'': ['*']}

install_requires = \
['czifile>=2019.7.2,<2020.0.0',
 'highdicom>=0.15.0,<0.16.0',
 'imagecodecs>=2021.8.26,<2022.0.0',
 'numpy>=1.21.2,<2.0.0',
 'openslide-python>=1.1.2,<2.0.0',
 'opentile>=0.3.0,<0.4.0',
 'pydicom>=2.2.1,<3.0.0',
 'wsidicom>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['wsidicomizer = wsidicomizer.cli:main']}

setup_kwargs = {
    'name': 'wsidicomizer',
    'version': '0.2.0',
    'description': 'Tool for converting wsi-files to DICOM',
    'long_description': "# *wsidicomizer*\n*wsidicomizer* is a Python library for converting files wsi files to DICOM. The aims of the project are:\n- Provide lossless conversion for files supported by opentile.\n- Provide 'as good as possible' conversion for other formats.\n- Simplify the encoding of wsi metadata into DICOM.\n\n# Supported formats\n*wsidicomizer* currently supports the following formats:\n- Aperio svs (lossless)\n- Hamamtsu ndpi (lossless)\n- Hamamatsu vms (lossy)\n- Philips tiff (lossless)\n- Mirax mrxs (lossy)\n- Trestle tiff (lossy)\n- Ventana bif (lossy)\n- Zeiss czi (lossy, only base level)\n\n## Installation\n***Download wsidicomizer from git***\n```console\n$ pip install wsidicomizer\n```\n\n***Install OpenSlide***\nInstructions for how to install OpenSlide is avaiable on https://openslide.org/download/\nFor Windows, you need also need add OpenSlide's bin-folder to the environment variable 'OPENSLIDE'\n\n***Install libjpeg-turbo***\nInstall libjpeg-turbo either as binary from https://libjpeg-turbo.org/ or using your package manager.\nFor Windows, you also need to add libjpeg-turbo's bin-folder to the environment variable 'TURBOJPEG'\n\n## Important note\nPlease note that this is an early release and the API is not frozen yet. Function names and functionality is prone to change.\n\n## Requirements\n*wsidicomizer* requires python >=3.7 and uses numpy, pydicom, highdicom, imagecodecs, openslide-python, PyTurboJPEG, opentile, and wsidicom.\n\n## Limitations\nFiles with z-stacks or multiple focal paths are currently not supported. DICOM properties related to slice thickness, focal plane thickness, and imaged volume are saved as 0 and not with proper values.\n\n## Basic cli-usage\n***Convert a wsi-file into DICOM using cli-interface***\n```console\nwsidicomizer -i 'path_to_wsi_file' -o 'path_to_output_folder'\n```\n### Arguments:\n~~~~\n-i, --input, path to input wsi file\n-o, --output, path to output folder\n-t, --tile-size, required depending on input format\n-d, --dataset, optional path to json file defining base dataset\n-l, --levels, optional levels to include\n-w, --workers, number of threads to use\n--chunk-size, number of tiles to give each worker at a time\n--format, encoding format to use if re-encoding. 'jpeg' or 'jpeg2000'\n--quality, quality to use if re-encoding.\n--subsampling, subsampling option to use if re-encoding.\n~~~~\n### Flags\n~~~~\n--no-label, do not include label(s)\n--no-overview, do not include overview(s)\n--no-confidential, do not include confidential metadata from image\n~~~~\nUsing the no-confidential-flag properties according to [DICOM Basic Confidentiality Profile](https://dicom.nema.org/medical/dicom/current/output/html/part15.html#table_E.1-1) are not included in the output file. Properties otherwise included are currently:\n* Acquisition DateTime\n* Device Serial Number\n\n## Basic notebook-usage\n***Create module datasets (Optional)***\n```python\nfrom wsidicomizer.dataset import create_device_module, create_sample, create_specimen_module, create_brightfield_optical_path_module, create_patient_module, create_study_module\ndevice_module = create_device_module(\n    manufacturer='Scanner manufacturer',\n    model_name='Scanner model name',\n    serial_number='Scanner serial number',\n    software_versions=['Scanner software versions']\n)\nsample = create_sample(\n    sample_id='sample id',\n    embedding_medium='Paraffin wax',\n    fixative='Formalin',\n    stainings=['hematoxylin stain', 'water soluble eosin stain']\n)\nspecimen_module = create_specimen_module(\n    slide_id='slide id',\n    samples=[sample]\n)\noptical_module = create_brightfield_optical_path_module()\npatient_module = create_patient_module()\nstudy_module = create_study_module()\n\n```\n\n***Convert a wsi-file into DICOM using python-interface***\n```python\nfrom wsidicomizer import WsiDicomizer\ncreated_files = WsiDicomizer.convert(\n    path_to_wsi_file,\n    path_to_output_folder,\n    [device_module, specimen_module, optical_module, patient_module, study_module],\n    tile_size\n)\n```\ntile_size is required for Ndpi- and OpenSlide-files.\n\n***Import a wsi file as a WsiDicom object.***\n```python\nfrom wsidicomizer import WsiDicomizer\nwsi = WsiDicomizer.open(path_to_wsi_file)\nregion = wsi.read_region((1000, 1000), 6, (200, 200))\nwsi.close()\n```\n\n## Other DICOM python tools\n- [pydicom](https://pydicom.github.io/)\n- [highdicom](https://github.com/MGHComputationalPathology/highdicom)\n- [wsidicom](https://github.com/imi-bigpicture/wsidicom)\n\n## Contributing\nWe welcome any contributions to help improve this tool for the WSI DICOM community!\n\nWe recommend first creating an issue before creating potential contributions to check that the contribution is in line with the goals of the project. To submit your contribution, please issue a pull request on the imi-bigpicture/wsidicomizer repository with your changes for review.\n\nOur aim is to provide constructive and positive code reviews for all submissions. The project relies on gradual typing and roughly follows PEP8. However, we are not dogmatic. Most important is that the code is easy to read and understand.\n\n## TODOs\n* Packaging of libjpeg-turbo into an 'ready-to-use' distribution.\n* Look into if OpenSlide python will provide a 'ready-to-use' distribution.\n* Interface for coding annotations (geometrical, diagnosis using for example structured reporting).\n\n## Acknowledgement\n*wsidicomizer*: Copyright 2021 Sectra AB, licensed under Apache 2.0.\n\nThis project is part of a project that has received funding from the Innovative Medicines Initiative 2 Joint Undertaking under grant agreement No 945358. This Joint Undertaking receives support from the European Union’s Horizon 2020 research and innovation programme and EFPIA. IMI website: www.imi.europa.eu",
    'author': 'Erik O Gabrielsson',
    'author_email': 'erik.o.gabrielsson@sectra.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/imi-bigpicture/wsidicomizer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
