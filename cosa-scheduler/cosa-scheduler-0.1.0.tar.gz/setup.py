# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cosa']

package_data = \
{'': ['*'],
 'cosa': ['configs/arch/*',
          'configs/mapspace/*',
          'configs/workloads/alexnet_graph/*',
          'configs/workloads/alexnet_pad_graph/*',
          'configs/workloads/deepbench_graph/*',
          'configs/workloads/densenet161_graph/*',
          'configs/workloads/dlrm_graph/*',
          'configs/workloads/resnet50_graph/*',
          'configs/workloads/resnext50_32x4d_graph/*',
          'configs/workloads/vgg16_graph/*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'gurobipy>=9.5.1,<10.0.0', 'numpy>=1.22.3,<2.0.0']

entry_points = \
{'console_scripts': ['cosa = cosa.cosa:run_cosa']}

setup_kwargs = {
    'name': 'cosa-scheduler',
    'version': '0.1.0',
    'description': 'A constrained-optimization based scheduler for spatial DNN accelerators',
    'long_description': 'None',
    'author': 'Qijing Huang',
    'author_email': 'qijing.huang@berkeley.edu',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
