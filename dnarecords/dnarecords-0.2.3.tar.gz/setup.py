# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dnarecords']

package_data = \
{'': ['*']}

install_requires = \
['fastparquet>=0.8.1,<0.9.0',
 'hail>=0.2.94,<0.3.0',
 'pyarrow>=8.0.0,<9.0.0',
 'tensorflow>=2.6.0,<3.0.0']

setup_kwargs = {
    'name': 'dnarecords',
    'version': '0.2.3',
    'description': 'Genomics data ML ready',
    'long_description': "# DNARecords\n\n[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)\n![example workflow](https://github.com/amanas/dnarecords/actions/workflows/ci-cd.yml/badge.svg)\n[![codecov](https://codecov.io/gh/amanas/dnarecords/branch/main/graph/badge.svg)](https://codecov.io/gh/amanas/dnarecords)\n![pylint Score](https://mperlet.github.io/pybadge/badges/9.97.svg)\n[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)\n\n**Genomics data ML ready.**\n\nTransform your vcf, bgen, etc. genomics datasets into a sample wise format so that you can use it \nfor Deep Learning models. \n\n## Installation\n\nDNARecords package has two main dependencies:\n\n* **Hail**, if you are transforming your genomics data into DNARecords\n* **Tensorflow**, if you are using a previously DNARecords dataset, for example, to train a DL model\n\nAs you may know, Tensorflow and Spark does not play very well together on a cluster with more than one machine.\n\nHowever, `dnarecords` package needs to be installed **only on the driver machine** of a Hail cluster.\n\nFor that reason, we recommend following these installation tips.\n\n### **On a dev environment**\n\n```bash\n$ pip install dnarecords\n```\n\nFor further details (or any trouble), review [Local environments](LOCAL_ENVS.md) section.\n\n### **On a Hail cluster or submitting a job to it**\n\nYou will already have Pyspark installed and will not intend to install Tensorflow. \n\nSo, just install dnarecords without dependencies on the driver machine. \n\nThere will be no missing modules as soon as you use the classes and functionality intended for Spark.\n\n```bash\n$ /opt/conda/miniconda3/bin/python -m pip install dnarecords --no-deps\n```\n*Note: assuming Hail python executable is /opt/conda/miniconda3/bin/python* \n\n### **On a Tensorflow environment or submitting a job to it**\n\nYou will already have Tensorflow installed and will not intend to install Pyspark. \n\nSo, just install dnarecords without dependencies. \n\nThere will be no missing modules as soon as you use the classes and functionality intended for Tensorflow.\n\n```bash\n$ pip install dnarecords --no-deps\n```\n\n\n## Working on Google Dataproc\n\nJust use and initialization action that installs `dnarecords` without dependencies.\n\n```bash\n$ hailctl dataproc start dnarecords --init gs://dnarecords/dataproc-init.sh\n```\nIy you need to work with other cloud providers, refer to [Hail docs](https://hail.is/docs/0.2/getting_started.html).\n\n## Usage\n\nIt is quite straightforward to understand the functionality of the package.\n\nGiven some genomics data, you can transform it into a **DNARecords Dataset** this way:\n\n\n```python\nimport dnarecords as dr\n\n\nhl = dr.helper.DNARecordsUtils.init_hail()\nhl.utils.get_1kg('/tmp/1kg')\nmt = hl.read_matrix_table('/tmp/1kg/1kg.mt')\nmt = mt.annotate_entries(dosage=hl.pl_dosage(mt.PL))\n\ndnarecords_path = '/tmp/dnarecords'\nwriter = dr.writer.DNARecordsWriter(mt.dosage)\nwriter.write(dnarecords_path, sparse=True, sample_wise=True, variant_wise=True,\n             tfrecord_format=True, parquet_format=True,\n             write_mode='overwrite', gzip=True)\n```\n\n\nGiven a DNARecords Dataset, you can read it as **Tensorflow Datasets** this way:\n\n```python\nimport dnarecords as dr\n\n\ndnarecords_path = '/tmp/dnarecords'\nreader = dr.reader.DNARecordsReader(dnarecords_path)\nsamplewise_ds = reader.sample_wise_dataset()\nvariantwise_ds = reader.variant_wise_dataset()\n```\n\nOr, given a DNARecords Dataset, you can read it as **Pyspark DataFrames** this way:\n\n\n```python\nimport dnarecords as dr\n\n\ndnarecords_path = '/tmp/dnarecords'\nreader = dr.reader.DNASparkReader(dnarecords_path)\nsamplewise_df = reader.sample_wise_dnarecords()\nvariantwise_df = reader.variant_wise_dnarecords()\n```\n\nWe will provide more examples and integrations soon.\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`dnarecords` was created by Atray Dixit, Andrés Mañas Mañas, Lucas Seninge. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`dnarecords` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n",
    'author': 'Atray Dixit, Andrés Mañas Mañas, Lucas Seninge',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
