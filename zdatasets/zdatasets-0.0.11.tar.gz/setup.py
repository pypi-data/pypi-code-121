# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datasets',
 'datasets.plugins',
 'datasets.plugins.batch',
 'datasets.plugins.executors',
 'datasets.tests',
 'datasets.tests.utils',
 'datasets.tutorials',
 'datasets.utils']

package_data = \
{'': ['*'],
 'datasets.tests': ['data/train/date=2020-07-23/region=king/*',
                    'data/train/date=2020-07-23/region=la/*']}

install_requires = \
['awswrangler>=2.12.0',
 'click>=7.0,<8.1',
 'importlib-metadata>=4.8.1',
 'pandas>=1.4.0',
 'pyarrow>=6.0.0',
 's3fs>=2022.1.0']

extras_require = \
{'dask': ['dask>=2021.9.1'], 'spark': ['pyspark>=3.2.0,<4.0.0']}

entry_points = \
{'datasets.executors': ['metaflow_executor = '
                        'datasets.plugins:MetaflowExecutor'],
 'datasets.plugins': ['batch_dataset = datasets.plugins:BatchDataset',
                      'flow_dataset = datasets.plugins:FlowDataset',
                      'hive_dataset = datasets.plugins:HiveDataset']}

setup_kwargs = {
    'name': 'zdatasets',
    'version': '0.0.11',
    'description': 'Dataset SDK for consistent read/write [batch, online, streaming] data.',
    'long_description': '![Tests](https://github.com/zillow/datasets/actions/workflows/test.yml/badge.svg)\n[![Coverage Status](https://coveralls.io/repos/github/zillow/datasets/badge.svg)](https://coveralls.io/github/zillow/datasets)\n[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/zillow/datasets/main?urlpath=lab/tree/datasets/tutorials)\n\n\nWelcome to @datasets\n==================================================\n\nTODO\n\n```python\nimport pandas as pd\nfrom metaflow import FlowSpec, Parameter, current, step\n\nfrom datasets import DatasetType, Mode\n\n\n# Can also invoke from CLI:\n#  > python datasets/tutorials/0_hello_dataset_flow.py run \\\n#    --hello_dataset \'{"name": "foo", "partition_by": "region", "mode": "Write"}\'\nclass HelloDatasetFlow(FlowSpec):\n    hello_dataset = Parameter(\n        "hello_dataset",\n        default=dict(name="HelloDataset", partition_by="region", mode=Mode.Write),\n        type=DatasetType,\n    )\n\n    @step\n    def start(self):\n        df = pd.DataFrame({"region": ["A", "A", "A", "B", "B", "B"], "zpid": [1, 2, 3, 4, 5, 6]})\n        print("saving df: \\n", df.to_string(index=False))\n\n        # Example of writing to a dataset\n        print(f"{self.hello_dataset.program_name=}")\n        self.hello_dataset.write(df)\n\n        self.next(self.end)\n\n    @step\n    def end(self):\n        print(f"I have dataset \\n{self.hello_dataset=}")\n\n    # hello_dataset to_pandas()\n    df: pd.DataFrame = self.hello_dataset.to_pandas(run_id=current.run_id)\n    print("self.hello_dataset.to_pandas():\\n", df.to_string(index=False))\n\n    # save this as an output dataset\n    self.output_dataset = self.hello_dataset\n\n\nif __name__ == "__main__":\n    HelloDatasetFlow()\n```\n',
    'author': 'Taleb Zeghmi',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
