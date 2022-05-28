# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mlfoundry',
 'mlfoundry.artifact',
 'mlfoundry.background',
 'mlfoundry.cli',
 'mlfoundry.cli.commands',
 'mlfoundry.dataset',
 'mlfoundry.dataset.whylogs_types',
 'mlfoundry.frameworks',
 'mlfoundry.inference',
 'mlfoundry.inference.store',
 'mlfoundry.inference.store.repositories',
 'mlfoundry.integrations',
 'mlfoundry.log_types',
 'mlfoundry.metrics',
 'mlfoundry.metrics.v1',
 'mlfoundry.metrics.v2',
 'mlfoundry.tracking',
 'mlfoundry.tracking.entities',
 'mlfoundry.vendor',
 'mlfoundry.vendor.pynvml',
 'mlfoundry.webapp']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.26,<4.0.0',
 'PyMySQL>=1.0.2,<2.0.0',
 'SQLAlchemy>=1.4.30,<2.0.0',
 'amplitude-tracker>=0.0.7,<0.0.8',
 'boto3>=1.14.1',
 'cryptography>=36.0.1,<37.0.0',
 'fastparquet>=0.7.2,<0.8.0',
 'human-id>=0.2.0,<0.3.0',
 'importlib-metadata>=4.11.3,<5.0.0',
 'matplotlib>=3.0.3',
 'numpy>=1.17.0',
 'orjson>=3.6.5,<4.0.0',
 'packaging>=21.3,<22.0',
 'pandas>=1.0.0',
 'pipreqs>=0.4.11,<0.5.0',
 'protobuf>=3.12.4,<4.0.0',
 'psutil>=5.9.0,<6.0.0',
 'psycopg2-binary>=2.9.1,<3.0.0',
 'pyarrow>=5.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'scipy>=1.5.4,<2.0.0',
 'shap>=0.40.0,<0.41.0',
 'tfy-mlflow-client==0.0.8',
 'tinynetrc>=1.3.1,<2.0.0',
 'whylogs>=0.6.15']

entry_points = \
{'console_scripts': ['mlfoundry = '
                     'mlfoundry.cli.cli_interface:create_mlfoundry_cli']}

setup_kwargs = {
    'name': 'mlfoundry',
    'version': '0.3.19',
    'description': 'Building logger package',
    'long_description': "# MlFoundry\n\n![](https://github.com/MyName/my-project/workflows/Project%20Tests/badge.svg)\n\nThis guide is to give an idea of how you can log metrics, paramaters, predictions, models, dataset using MlFoundry. MlFoundry supports logging above mentioned logs to S3 asynchronously.\n\n## API Workflow:\n\nUsing mlfoundry you ca create multiple projects and each projects can have multiple run.\n\n**Example**\n\n1. Project 1\n   - run 1\n   - run 2\n2. Project 2\n   - run 1\n   - run 2\n   - run 3\n   - run 4\n\nEach run under each project will have a unique run_id.\n\n## Quickstart\n\n### 1. Install mlfoundry\n\n```\n# Install via pip\npip install mlfoundry --extra-index-url https://api.packagr.app/public\n```\n\n### 2. Setup AWS credentials\n\nTo setup AWS credentials MlLogs_foundry's CLI can be used. AWS credentials are required to store the artifacts like model, dataset, whylogs_metrics etc in S3 Bucket.\n\nThe CLI requires AWS credentials(SECRET_ACCESS_KEY, ACCESS_KEY_ID)\n\nAll the credentials can be set by running:\n\n`mlfoundry init`\n\n### 3. Initialise mlfoundry\n\nCreate an project and use the project_name to create a run:\n\n```python\n import mlfoundry as mlf\n\n # create a run\n mlf_run = mlf.create_run(project_name=<project-name>)\n```\n\nIf you want to use a previously created run:\n\n```python\n# printing all the runs available and get the run_id\nshow_all_runs()\n\nrun = get_run(run_id=<run_id>)\n```\n\n### 4. Start logging\n\n**To log a model:**\n\n```python\nrun.log_model(sklearn_model, framework=mlf.ModelFramework.SKLEARN)\n```\n\n**To log parameters:**\n\n```python\nrun.log_params({'learning_rate':0.01,\n                  'n_epochs:10'\n                  })\n```\n\n**To log metrics:**\n\n```python\nrun.log_metrics({'accuracy':87,\n                  'f1_score':0.84,\n                  })\n```\n\n**Log predictions synchronously:**\n\nfeature_df: a pd.DataFrame, the input given to the model to make predictions\n\npredictions: must be a list or pd.Series\n\nTo log predictions synchronously:\n\n```python\nrun.log_predictions(self, feature_df, predictions)\n```\n\nTo log predictions asynchronously:\n\n```python\nresponses = run.log_predictions_async(self, feature_df, predictions)\n\n#### To confirm that the log request completed successfully, await for futures to resolve: This is a blocking call\nimport concurrent.futures as cf\nfor response in cf.as_completed(responses):\n  res = response.result()\n```\n\nUsers can additionaly pass in feature_names argument which is a list of feture names for feature_df.\n\n# To release as Python package\n\nUse Github Releases to create a tag on main and release it. This will trigger the workflow and publish the pip package\n\nTags must be of format `vx.x.x`, example `v0.1.0`\n\n# Development instructions\n\n```\ngit clone https://github.com/truefoundry/mlfoundry.git\ncd mlfoundry\nvirtualenv venv\nsource venv/bin/activate\npip install poetry\npoetry install\npre-commit install\n```\n\n# Run Manual QA\n```\ngit clone https://github.com/truefoundry/mlf-test\ncd mlf-test\nvirtualenv venv\nsource venv/bin/activate\npip install -r requirements.txt\ncd mlf_examples\npython main.py  In-this-step-check-for-error-logs\nmlfoundry ui  In-this-step-go-to-the-listed-url-and-play-around-with-the-ui\n```\n",
    'author': 'Abhishek Choudhary',
    'author_email': 'abhichoudhary06@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/truefoundry/mlfoundry',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
