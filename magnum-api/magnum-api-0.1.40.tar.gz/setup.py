# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['magnumapi',
 'magnumapi.geometry',
 'magnumapi.geometry.blocks',
 'magnumapi.geometry.definitions',
 'magnumapi.geometry.primitives',
 'magnumapi.matpro',
 'magnumapi.plotting',
 'magnumapi.tool_adapters',
 'magnumapi.tool_adapters.ansys']

package_data = \
{'': ['*']}

install_requires = \
['Shapely>=1.8.2,<2.0.0',
 'ansys-mapdl-core>=0.61.6,<0.62.0',
 'ansys-mapdl-reader>=0.51.11,<0.52.0',
 'ipyaggrid>=0.2.2,<0.3.0',
 'matplotlib>=3.5.2,<4.0.0',
 'numpy>=1.22.4,<2.0.0',
 'opencv-python>=4.5.5,<5.0.0',
 'pandas>=1.4.2,<2.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'pymbse-commons>=0.0.2,<0.0.3',
 'pyvista>=0.34.1,<0.35.0',
 'roxie-api>=0.0.3,<0.0.4']

setup_kwargs = {
    'name': 'magnum-api',
    'version': '0.1.40',
    'description': '',
    'long_description': '# Project Overview\nThe CHART MagNum (Magnum Numerics) aims at introducing advanced design techniques in order to support the design process of superconducting accelerator magnet.\nThe project responds to the following strategic goals:\n- Sustainability\n\n  Ensure that outstanding modeling work will have an impact on present or future designs. This also require that models have clearly defined scope and range of applicability.\n- Traceability\n\n  Ensure that the modeler is able to trace back the input parameters, code and script versions, etc., that have been used to produce a particular plot in a ppt or pdf.\n  Traceability is even more important in multi-scale and multi-model analysis.\n- Repeatability\n\n  Ensure that results presented at, e.g., a Conceptual Design Review can be reproduced at any later time.\n  Ensure that as-built models can be re-run at any moment during a potentially decades-long project life cycle.\n- Flexibility\n\n  Allow for different labs and collaborators to have/prefer different licenses.\n  Enable researchers to implement innovative ideas while building upon existing best practices, but without having to solve legacy issues.\n- Usability\n\n  Encapsulate the increased flexibility behind easy-to-use UIs for the standard design work.\n\nThe project implements a number of concepts introduced by the MBSE (Model-Based System Engineering) methdology.\nIn particular, MBSE shifts the focus from documents to models as primary means of communication in complex system design projects.\n\n# Project Architecture\nThe project is composed of two parts: notebooks and a library with an API (Application Programming Interface).\nA notebook combines documentation with source code and results of its execution. As such, it encodes a design step that involves model construction from a parametrized input, its execution and extraction of the figures of merit.\nIn order to keep the notebooks lean and linear, the model control logic is extracted to the API.\nAn important pillar of the framework is automation of the modelling process; the automation is achieved with GitLab CI pipelines. To this end, a set of notebooks representing a design process are concatenated into a design workflow.\nThe workflow is executed for a given model input. The input contains generic part (e.g., material properties, geometry, cable parameters) and model-specific part (e.g., electromagnetic boundary condidtions, definition of mechanical contacts).\nAs a result, a workflow is immediatelly suited for design optimization, co-simulation, parametric studies, etc.\n\n# User Guide\nIn the following we discuss the steps needed to obtain and further develop the API. In addition,\nthe main modules of `magnum-api` are presented:\n- Geometry\n- Tool Adapters\n- Optimization\n- Material Properties\n- Plotting\n\n## Getting Started\nThe project is developed with Python 3.6+ and was tested on Windows and Linux machines.\nThe python project dependencies are stored in `requirements.txt` file and need to be installed prior to API execution.\nIn order to execute tool adapters for ROXIE and ANSYS, both need to be installed. The API supports ROXIE 10.3 and ANSYS 2020R1.\nThe code development can be carried out with any IDE (Integrated Development Environment) and the suggested one is PyCharm.\nPlease consult `CONTRIBUTING.md` file for contribution guidelines.\n\n## Geometry\nThe geometry module provides classes to handle coil geometry. So far, the 2D cos-theta geometry is implemented.\nWe follow the ROXIE block definition and reuse the cable data concept. The block definition supports absolute and relative angle definition. The geometry input can be expressed as a list of dictionaries and a pandas DataFrame either as objects or, respectively as json and csv files.\n\n- geometry creation with json file for absolute angle definition\n\n```python\nfrom magnumapi.cadata.CableDatabase import CableDatabase\nfrom magnumapi.geometry.CosThetaGeometry import CosThetaGeometry\n\njson_path = \'input/16T_abs.json\'\ncadata_path = \'input/roxieold_2.cadata\'\ncadata = CableDatabase(cadata_path)\n\ngeometry = CosThetaGeometry.with_roxie_absolute_angle_definition_json(json_path, cadata)\ngeometry.build_blocks()\ngeometry.plotly_geometry_blocks()\n```\n\n- geometry creation with json file for relative angle definition\n\n```python\nfrom magnumapi.cadata.CableDatabase import CableDatabase\nfrom magnumapi.geometry.CosThetaGeometry import CosThetaGeometry\n\njson_path = \'input/16T_rel.json\'\ncadata_path = \'input/roxieold_2.cadata\'\ncadata = CableDatabase(cadata_path)\n\ngeometry = CosThetaGeometry.with_roxie_relative_angle_definition_json(json_path, cadata)\ngeometry.build_blocks()\ngeometry.plotly_geometry_blocks()\n```\n\nThe remaining methods are presented in the UML diagram below.\n<img src="figures/CosThetaGeometryUMLClassDiagram.PNG">\n\n## Tool Adapters\nA tool adapter provides methods to control a simulation tool. So far, we support ROXIE and ANSYS as show in the diagram below. \n<img src="figures/CosThetaGeometryUMLClassDiagram.PNG">\n\n## Optimization\n\nWe implement a genetic optimization algorithm that operates with modelling workflows implemented as notebooks.\nThe optimization algorithm works as follows:\n1. Load design variables table with allowed range of values, its type, and number of bits per variable\n2. Load optimization config\n3. Load an input model parameter that is updated during the optimization process. Each notebook relies on this input.\n4. Randomly initialize starting population of individuals\n5. For each generation:\n  - Evaluate fitness function for each notebook (in case of errors, a penalty value is applied)\n  - Perform tournament selection for mating (if elitism is considered)\n  - Execute crossover operator\n  - Execute mutation operator\n\n### Design Variables Table\nBelow we present a sample design variables table. The meaning of columns is\n- xl: lower value of a variable\n- xu: upper value of a variable\n- xs: starting value of a variable\n- variable: variable name\n- variable_type: numeric variable type\n- bits: bits per variable\n- bcs: block index\n\n| xl        | xu           | xs  | variable | variable_type | bits | bcs |\n| ------------- |-------------| -----| ---- | ------------- | ---- | --- |\n| 0 | 3.0 | 10.0 | 3 | phi_r | float | 6 | 2 |\n| 1 | 3.0 | 10.0 | 3 | phi_r | float | 6 | 3 |\n| 2 | 3.0 | 10.0 | 3 | phi_r | float | 6 | 4 |\n| 3 | 3.0 | 10.0 | 3 | phi_r | float | 6 | 6 |\n| 4 | 3.0 | 10.0 | 3 | phi_r | float | 6 | 7 |\n\n### Optimization Config\nOptimization algorithm is parametrized with a config. The config is represented as a json file.\nA sample config is shown below. The meaning of keys is:\n- input_folder: an absolute path to an input folder\n- output_folder: an absolute path to an output folder\n- notebooks: a list of notebook configs\n  - notebook_folder: relative notebook folder path\n  - notebook_name: full notebook name\n  - input_parameters: dictionary of parameters; key is a name for the target notebook and the value is the name from a source notebook\n  - output_parameters: list of output parameters\n  - input_artefacts: dictionary of parameters; key is a relative artefact path for the target notebook and the value is the relative artefact path from a source notebook\n  - output_artefacts: list of output artefacts\n\n```json\n{\n  "input_folder": "/home/mmaciejewski/gitlab/magnum-nb/",\n  "output_folder": "/home/mmaciejewski/gitlab/magnum-nb/output/",\n  "notebooks": [\n    {\n      "notebook_folder": "geometry",\n      "notebook_name": "Geometry.ipynb",\n      "input_parameters": {},\n      "output_parameters": [],\n      "input_artefacts": {},\n      "output_artefacts": []\n    },...\n  ]\n}\n```\n\n## Material Properties\n\nWe implemented the following material properties:\n\n- resistivities:\n  - calc_rho_cu_nist\n- heat capacities:\n  - calc_cv_cu_nist\n  - calc_cv_nb3sn_nist\n- critical current fits:\n  - calc_jc_nbti_bottura\n  - calc_jc_nb3sn_bordini\n  - calc_jc_nb3sn_summers\n  - calc_jc_nb3sn_summers_orig\n\n## Plotting\nPlotting module contains generic plotting functions. \n',
    'author': 'mmaciejewski',
    'author_email': 'michal.maciejewski@ief.ee.ethz.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.cern.ch/chart-magnum/magnum-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
