# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scriptflow']

package_data = \
{'': ['*']}

install_requires = \
['asyncssh>=2.9.0,<3.0.0',
 'click>=8.0.3,<9.0.0',
 'omegaconf>=2.1.1,<3.0.0',
 'pytest>=7.1.1,<8.0.0',
 'requests>=2.27.1,<3.0.0',
 'rich>=11.0.0,<12.0.0',
 'tinydb>=4.7.0,<5.0.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['scriptflow = scriptflow.cli:cli']}

setup_kwargs = {
    'name': 'scriptflow',
    'version': '0.2.2',
    'description': 'Like a makefile but in python, a stripped-down system of Airflow or Luigi',
    'long_description': '# scriptflow\n\n[![CircleCI](https://circleci.com/gh/tlamadon/scriptflow/tree/main.svg?style=svg)](https://circleci.com/gh/tlamadon/scriptflow/tree/main) [![PyPI version](https://badge.fury.io/py/scriptflow.svg)](https://badge.fury.io/py/scriptflow) [![codecov](https://codecov.io/gh/tlamadon/scriptflow/branch/main/graph/badge.svg?token=0E8J7635HD)](https://codecov.io/gh/tlamadon/scriptflow)\n\nSmall library that allows scheduling scripts asyncrhonously on different platforms. Think of it as a Make when you can write the dependencies as python code, and that can run locally, on an HPC or in the cloud (cloud is not implemented just yet).\n\nThe status is very experimental. I will likely be changing the interface as I go. \n\n## Goals:\n\n - [x] works on windows / osx / linux\n - [x] describe dependencies as python code (using await/async)\n - [x] describe scripts with input/output as code\n - [x] clean terminal feedback (using rich)\n - [x] task retry\n - [x] check that output was generated \n - [x] notifications (using light webserver at [scriptflow.lamadon.com](http://scriptflow.lamadon.com/) )\n - [x] send status to central web service\n - [x] resume flows\n - [ ] clean output\n - [ ] named runs\n - [x] store run information\n - [x] output diagnostic / reporting (tracing how files were created)\n - [x] simpler interface with default head executor and awaitable tasks\n - [x] skip computation based on timestamp of inputs and outpus\n - [ ] load and store tasks results\n - [ ] remove existing output of task if task is started (issue with failing tasks that look like they worked)\n - executors :\n   - [x] local excutor using subprocess \n   - [x] HPC excutor (monitoring qsub) \n   - [ ] docker Executor \n   - [ ] aws executor (probably using Ray)\n   - [ ] dask executor  \n - [x] add check on qsub return values\n - [x] select flow by name from terminal \n - [ ] ? scripts can create tasks, not sure how to await them. \n - reporting:\n   - [ ] input and output hashes\n   - [x] start and end datetimes\n - notification system\n   - [x] allow to send messages\n   - [ ] allow for runs\n   - [ ] allow to send messages with html content like images\n - writing tasks and flows \n   - [ ] cache flows in addition to caching tasks (avoid same task getting scheduled from 2 places)\n   - [ ] a functional api for task creation with hooks\n   - [ ] a functional api for flows\n   - [ ] controller could parse the log file for results (looking for specific triggers)\n   - [ ] allow for glob output/input\n   - [ ] provide simple toml/json interface for simple tasks and flows\n   - [x] use `shlex` to parse command from strings\n - cli\n   - [ ] pass arguments to flows \n   - [ ] create portable executable\n\n\n## Simple flow example:\n\nCreate a file `sflow.py` with:\n\n```python\nimport scriptflow as sf\n\n# set main options\nsf.init({\n    "executors":{\n        "local": {\n            "maxsize" : 5\n        } \n    },\n    \'debug\':True\n})\n\n# example of a simple step that combines outcomes\ndef step2_combine_file():\n    with open(\'test_1.txt\') as f:\n        a = int(f.readlines()[0])\n    with open(\'test_2.txt\') as f:\n        b = int(f.readlines()[0])\n    with open(\'final.txt\',\'w\') as f:\n        f.write("{}\\n".format(a+b))\n\n# define a flow called sleepit\nasync def flow_sleepit():\n\n    i=1\n    t1 = sf.Task(\n      cmd    = f"""python -c "import time; time.sleep(5); open(\'test_{i}.txt\',\'w\').write(\'5\');" """,\n      output = f"test_{i}.txt",\n      name   = f"solve-{i}")\n\n    i=2\n    t1 = sf.Task(\n      cmd    = f"""python -c "import time; time.sleep(5); open(\'test_{i}.txt\',\'w\').write(\'5\');" """,\n      output = f"test_{i}.txt",\n      name   = f"solve-{i}")\n\n    await sf.bag(t1,t2)\n\n    tfinal = sf.Task("python -c \'import sflow; sflow.step2_combine_file()\'")\n    tfinal.output(f"final.txt").uid(f"final").add_deps([t1.output_file,t2.output_file])\n    await tfinal\n```        \n\nthen create a local env, activate, install and run!\n\n```shell\npython3 -m venv env\nsource env/bin/activate\npip install scriptflow\nscritpflow run sleepit\n```\n\n## Life cycle of a task\n\n1. the task object is created. All properties can be edited.\n2. the task is sent to an executor. At this point, the properties of the task are frozen. They can be read, copied but not changed. A unique ID id created from the task from its command and its inputs. The task can be sent by using the `start()` method, or it will be sent automatically when awaited.\n3. the task is awaited, and hence execution is blocked until the task is finished. Nothing can be done at that stage. Again, the task is automatically sent at this stage if it has not be done before. Also note that several tasks can be awaited in parallel by bagging them with `sf.bag(...)`.\n4. the task is completed, the await returns. The task has now it\'s output attached to it, it can be used in the creation of other tasks.\n\n## Inspiration / Alternatives\n\nI have tried to use the following three alternatives which are all truly excelent!\n\n - [pydoit](https://pydoit.org/)\n - [nextflow](https://www.nextflow.io/)\n - [snakemake](https://snakemake.readthedocs.io/en/stable/)\n\nThere were use cases that I could not implement cleanly in the dataflow model of nextflow. I didn\'t like that snakemake relied on file names to trigger rules, I was constently juggling complicated file names. Pydoit is really great, but I couldn\'t find how to extend it to build my own executor, and I always found myself confused writing new tasks and dealing with dependencies. \n\n## Developing\n\nthe package is managed using poetry, install poetry first then \n\n```\npoetry install\n\n# run example\ncd examples/simple-local\npoetry run scriptflow run sleepit\n\n# run tests with coverate\npoetry run python -m pytest --cov=scriptflow\npoetry run coverage xml\npoetry run codecov -t <token>\n\n```\n\n\n\n\n### Docker images to try the different schedulers\n\n - [PBS](https://openpbs.atlassian.net/wiki/spaces/PBSPro/pages/79298561/Using+Docker+to+Instantiate+PBS)\n - [slurm](https://medium.com/analytics-vidhya/slurm-cluster-with-docker-9f242deee601)\n=======\n',
    'author': 'Thibaut Lamadon',
    'author_email': 'thibaut.lamadon@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tlamadon/scriptflow',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
