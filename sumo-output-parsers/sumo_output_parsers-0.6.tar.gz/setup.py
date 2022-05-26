# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sumo_output_parsers',
 'sumo_output_parsers.csv_based_parser',
 'sumo_output_parsers.definition_parser',
 'sumo_output_parsers.models',
 'sumo_output_parsers.tree_parser',
 'sumo_output_parsers.visualizer']

package_data = \
{'': ['*']}

install_requires = \
['Cython',
 'dataclasses',
 'h5py>=3.1.0,<4.0.0',
 'joblib',
 'lxml',
 'more_itertools',
 'nptyping>=1.4.1,<2.0.0',
 'numpy>=1.19.2,<2.0.0',
 'pandas>=1.1.3,<2.0.0',
 'requests',
 'scikit-learn>=1.0,<2.0',
 'scipy',
 'tabulate',
 'tqdm>=4.61.2,<5.0.0']

extras_require = \
{'full': ['hvplot>=0.7.3,<0.8.0',
          'moviepy<1.0.2',
          'Shapely>=1.7.0,<2.0.0',
          'pyproj>=3.0.0,<4.0.0',
          'SumoNetVis>=1.6.0,<2.0.0',
          'geopandas>=0.10.0,<0.11.0',
          'geoviews>=1.9.1,<2.0.0',
          'imageio-ffmpeg',
          'pyviz',
          'adjustText']}

setup_kwargs = {
    'name': 'sumo-output-parsers',
    'version': '0.6',
    'description': 'Fast and lightweight file parsers for SUMO(traffic simulator) output',
    'long_description': '# What\'s this?\n\nFast and lightweight file parsers for Eclipse SUMO(traffic simulator) output.\n\nThe SUMO outputs are huge in size and hard to handle.\n\nSUMO team provides scripts to convert from xml into CSV, however, the procedure is troublesome (downloading XSD, executing python script...)\n\nAlso, machine learning users take care of matrix data format.\n\nThis package provides an easy-to-call python interface to obtain matrix form from SUMO xml files.\n\n# Contributions\n\n- easy-to-call python interfaces to obtain matrix form from SUMO xml files\n- easy-to-call python interfaces to visualize SUMO simulations\n\n![Example of animation](https://user-images.githubusercontent.com/1772712/135924848-4a938dd2-b2d3-4dfe-bfd6-94904086c382.gif)\n\n# Install\n\n```\npip install sumo-output-parsers\n```\n\nSome submodules are not ready to use by default for which\nwe avoid errors relating Proproj or Cartopy. \n\nIf you\'d like to depict car flows or detector positions, install with\n\n```\npip install "sumo-output-parsers[full]"\n```\n\n# Sample\n\nSee `sample.py`\n\n# Test\n\n```\npytest tests/\n```\n\nIf your package-dependency is complete including packages for visualization, \nthen `pytest tests/ --visualization`\n\n\n# For developers\n\nBuild with poetry.\n\n# Install Guide\n\nWhen you encounter any dependency issues, I recommend to use `conda`.\n`cartopy` and `proj` cause the dependency issue frequently.\nConda helps you to install the compiled binaries.\nSee Proj [documentation](https://proj.org/install.html).\n\n# License\n\n```\n@misc{sumo-output-parsers,\n  author = {Kensuke Mitsuzawa},\n  title = {sumo_output_parsers},\n  year = {2021},\n  publisher = {GitHub},\n  journal = {GitHub repository},\n  howpublished = {\\url{}},\n}\n```',
    'author': 'Kensuke Mitsuzawa',
    'author_email': 'kensuke.mit@gmail.com',
    'maintainer': 'Kensuke Mitsuzawa',
    'maintainer_email': 'kensuke.mit@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
