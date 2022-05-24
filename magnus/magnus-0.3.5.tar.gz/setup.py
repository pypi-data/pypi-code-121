# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['magnus']

package_data = \
{'': ['*']}

install_requires = \
['click',
 'click-plugins>=1.1.1,<2.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'ruamel.yaml',
 'ruamel.yaml.clib',
 'stevedore>=3.5.0,<4.0.0',
 'yachalk']

extras_require = \
{'docker': ['docker'], 'notebook': ['papermill']}

entry_points = \
{'console_scripts': ['magnus = magnus.cli:cli'],
 'magnus.catalog.BaseCatalog': ['do-nothing = magnus.catalog:DoNothingCatalog',
                                'file-system = '
                                'magnus.catalog:FileSystemCatalog'],
 'magnus.datastore.BaseRunLogStore': ['buffered = '
                                      'magnus.datastore:BufferRunLogstore',
                                      'file-system = '
                                      'magnus.datastore:FileSystemRunLogstore'],
 'magnus.executor.BaseExecutor': ['demo-renderer = '
                                  'magnus.executor:DemoRenderer',
                                  'local = magnus.executor:LocalExecutor',
                                  'local-container = '
                                  'magnus.executor:LocalContainerExecutor'],
 'magnus.integration.BaseIntegration': ['demo-renderer-run_log_store-buffered '
                                        '= '
                                        'magnus.integration:DemoRenderBufferedRunLogStore',
                                        'local-catalog-do-nothing = '
                                        'magnus.integration:LocalDoNothingCatalog',
                                        'local-container-catalog-do-nothing = '
                                        'magnus.integration:LocalContainerDoNothingCatalog',
                                        'local-container-catalog-file-system = '
                                        'magnus.integration:LocalContainerComputeFileSystemCatalog',
                                        'local-container-run_log_store-buffered '
                                        '= '
                                        'magnus.integration:LocalContainerComputeBufferedRunLogStore',
                                        'local-container-run_log_store-file-system '
                                        '= '
                                        'magnus.integration:LocalContainerComputeFileSystemRunLogstore',
                                        'local-container-secrets-dotenv = '
                                        'magnus.integration:LocalContainerComputeDotEnvSecrets',
                                        'local-run_log_store-buffered = '
                                        'magnus.integration:LocalComputeBufferedRunLogStore',
                                        'local-run_log_store-file-system = '
                                        'magnus.integration:LocalComputeFileSystemRunLogStore'],
 'magnus.nodes.BaseNode': ['as-is = magnus.nodes:AsISNode',
                           'dag = magnus.nodes:DagNode',
                           'fail = magnus.nodes:FailNode',
                           'map = magnus.nodes:MapNode',
                           'parallel = magnus.nodes:ParallelNode',
                           'success = magnus.nodes:SuccessNode',
                           'task = magnus.nodes:TaskNode'],
 'magnus.secrets.BaseSecrets': ['do-nothing = '
                                'magnus.secrets:DoNothingSecretManager',
                                'dotenv = magnus.secrets:DotEnvSecrets'],
 'magnus.tasks.BaseTaskType': ['notebook = magnus.tasks:NotebookTaskType',
                               'python = magnus.tasks:PythonTaskType',
                               'python-lambda = '
                               'magnus.tasks:PythonLambdaTaskType',
                               'shell = magnus.tasks:ShellTaskType']}

setup_kwargs = {
    'name': 'magnus',
    'version': '0.3.5',
    'description': 'A Compute agnostic pipelining software',
    'long_description': '# Hello from magnus\n\nMagnus is a data science pipeline definition and execution tool. It provides a way to:\n\n- Define a pipeline steps and the flow.\n- Run the pipeline in any environment, local is default.\n- Store the run metadata and data catalogs and re-run in case of failures.\n\nOnce the pipeline is proven to be correct and functional in any environment, there is zero code change\nrequired to deploy it elsewhere. The behavior of the runs are identical in all environments. Magnus\nis not a queuing or scheduling engine, but delegates that responsibility to chosen deployment patterns.\n\n### Short Summary\n\nMagnus provides four capabilities for data teams:\n\n- **Compute execution plan**: A DAG representation of work that you want to get done. Individual nodes of the DAG\ncould be simple python or shell tasks or complex deeply nested parallel branches or embedded DAGs themselves.\n\n- **Run log store**: A place to store run logs for reporting or re-running older runs. Along with capturing the\nstatus of execution,  the run logs also capture code identifiers (commits, docker image digests etc), data hashes and\nconfiguration settings for reproducibility and audit.\n\n- **Data Catalogs**: A way to pass data between nodes of the graph during execution and also serves the purpose of\nversioning the data used by a particular run.\n\n- **Secrets**: A framework to provide secrets/credentials at run time to the nodes of the graph.\n\n### Design decisions:\n\n- **Easy to extend**: All the four capabilities are just definitions and can be implemented in many flavors.\n\n    - **Compute execution plan**: You can choose to run the DAG on your local computer, in containers of local computer\n    or off load the work to cloud providers or translate the DAG to AWS step functions or Argo workflows.\n\n    - **Run log Store**: The actual implementation of storing the run logs could be in-memory, file system, S3,\n    database etc.\n\n    - **Data Catalogs**: The data files generated as part of a run could be stored on file-systems, S3 or could be\n    extended to fit your needs.\n\n    - **Secrets**: The secrets needed for your code to work could be in dotenv, AWS or extended to fit your needs.\n\n- **Pipeline as contract**: Once a DAG is defined and proven to work in local or some environment, there is absolutely\nno code change needed to deploy it to other environments. This enables the data teams to prove the correctness of\nthe dag in dev environments while infrastructure teams to find the suitable way to deploy it.\n\n- **Reproducibility**: Run log store and data catalogs hold the version, code commits, data files used for a run\nmaking it easy to re-run an older run or debug a failed run. Debug environment need not be the same as\noriginal environment.\n\n- **Easy switch**: Your infrastructure landscape changes over time. With magnus, you can switch infrastructure\nby just changing a config and not code.\n\n\nMagnus does not aim to replace existing and well constructed orchestrators like AWS Step functions or\n[argo](https://argoproj.github.io/workflows/) but complements them in a unified, simple and intuitive way.\n\n## Documentation\n\n[More details about the project and how to use it available here](https://astrazeneca.github.io/magnus-core/).\n\n## Installation\n\n### pip\n\nmagnus is a python package and should be installed as any other.\n\n```shell\npip install magnus\n```\n\n# Example Run\n\nTo give you a flavour of how magnus works, lets create a simple pipeline.\n\nCopy the contents of this yaml into getting-started.yaml.\n\n---\n!!! Note\n\n   The below execution would create a folder called \'data\' in the current working directory.\n   The command as given should work in linux/macOS but for windows, please change accordingly.\n\n---\n\n``` yaml\ndag:\n  description: Getting started\n  start_at: step parameters\n  steps:\n    step parameters:\n      type: task\n      command_type: python-lambda\n      command: "lambda x: {\'x\': int(x) + 1}"\n      next: step shell\n    step shell:\n      type: task\n      command_type: shell\n      command: mkdir data ; env >> data/data.txt # For Linux/macOS\n      next: success\n      catalog:\n        put:\n          - "*"\n    success:\n      type: success\n    fail:\n      type: fail\n```\n\nSince the pipeline expects a parameter ```x```, lets provide that using ```parameters.yaml```\n\n```yaml\nx: 3\n```\n\nAnd let\'s run the pipeline using:\n``` shell\n magnus execute --file getting-started.yaml --parameters-file parameters.yaml\n```\n\nYou should see a list of warnings but your terminal output should look something similar to this:\n\n``` json\n{\n    "run_id": "20220118114608",\n    "dag_hash": "ce0676d63e99c34848484f2df1744bab8d45e33a",\n    "use_cached": false,\n    "tag": null,\n    "original_run_id": "",\n    "status": "SUCCESS",\n    "steps": {\n        "step parameters": {\n            "name": "step parameters",\n            "internal_name": "step parameters",\n            "status": "SUCCESS",\n            "step_type": "task",\n            "message": "",\n            "mock": false,\n            "code_identities": [\n                {\n                    "code_identifier": "c5d2f4aa8dd354740d1b2f94b6ee5c904da5e63c",\n                    "code_identifier_type": "git",\n                    "code_identifier_dependable": false,\n                    "code_identifier_url": "<INTENTIONALLY REMOVED>",\n                    "code_identifier_message": "<INTENTIONALLY REMOVED>"\n                }\n            ],\n            "attempts": [\n                {\n                    "attempt_number": 0,\n                    "start_time": "2022-01-18 11:46:08.530138",\n                    "end_time": "2022-01-18 11:46:08.530561",\n                    "duration": "0:00:00.000423",\n                    "status": "SUCCESS",\n                    "message": ""\n                }\n            ],\n            "user_defined_metrics": {},\n            "branches": {},\n            "data_catalog": []\n        },\n        "step shell": {\n            "name": "step shell",\n            "internal_name": "step shell",\n            "status": "SUCCESS",\n            "step_type": "task",\n            "message": "",\n            "mock": false,\n            "code_identities": [\n                {\n                    "code_identifier": "c5d2f4aa8dd354740d1b2f94b6ee5c904da5e63c",\n                    "code_identifier_type": "git",\n                    "code_identifier_dependable": false,\n                    "code_identifier_url": "<INTENTIONALLY REMOVED>",\n                    "code_identifier_message": "<INTENTIONALLY REMOVED>"\n                }\n            ],\n            "attempts": [\n                {\n                    "attempt_number": 0,\n                    "start_time": "2022-01-18 11:46:08.576522",\n                    "end_time": "2022-01-18 11:46:08.588158",\n                    "duration": "0:00:00.011636",\n                    "status": "SUCCESS",\n                    "message": ""\n                }\n            ],\n            "user_defined_metrics": {},\n            "branches": {},\n            "data_catalog": [\n                {\n                    "name": "data.txt",\n                    "data_hash": "8f25ba24e56f182c5125b9ede73cab6c16bf193e3ad36b75ba5145ff1b5db583",\n                    "catalog_relative_path": "20220118114608/data.txt",\n                    "catalog_handler_location": ".catalog",\n                    "stage": "put"\n                }\n            ]\n        },\n        "success": {\n            "name": "success",\n            "internal_name": "success",\n            "status": "SUCCESS",\n            "step_type": "success",\n            "message": "",\n            "mock": false,\n            "code_identities": [\n                {\n                    "code_identifier": "c5d2f4aa8dd354740d1b2f94b6ee5c904da5e63c",\n                    "code_identifier_type": "git",\n                    "code_identifier_dependable": false,\n                    "code_identifier_url": "<INTENTIONALLY REMOVED>",\n                    "code_identifier_message": "<INTENTIONALLY REMOVED>"\n                }\n            ],\n            "attempts": [\n                {\n                    "attempt_number": 0,\n                    "start_time": "2022-01-18 11:46:08.639563",\n                    "end_time": "2022-01-18 11:46:08.639680",\n                    "duration": "0:00:00.000117",\n                    "status": "SUCCESS",\n                    "message": ""\n                }\n            ],\n            "user_defined_metrics": {},\n            "branches": {},\n            "data_catalog": []\n        }\n    },\n    "parameters": {\n        "x": 4\n    },\n    "run_config": {\n        "executor": {\n            "type": "local",\n            "config": {}\n        },\n        "run_log_store": {\n            "type": "buffered",\n            "config": {}\n        },\n        "catalog": {\n            "type": "file-system",\n            "config": {}\n        },\n        "secrets": {\n            "type": "do-nothing",\n            "config": {}\n        }\n    }\n}\n```\n\nYou should see that ```data``` folder being created with a file called ```data.txt``` in it.\nThis is according to the command in ```step shell```.\n\nYou should also see a folder ```.catalog``` being created with a single folder corresponding to the run_id of this run.\n\nTo understand more about the input and output, please head over to the\n[documentation](https://project-magnus.github.io/magnus-core/).\n',
    'author': 'Vijay Vammi',
    'author_email': 'vijay.vammi@astrazeneca.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AstraZeneca/magnus-core',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
