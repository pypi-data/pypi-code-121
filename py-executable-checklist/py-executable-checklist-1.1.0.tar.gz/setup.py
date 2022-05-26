# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['py_executable_checklist']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'py-executable-checklist',
    'version': '1.1.0',
    'description': 'Helper classes to develop executable workflow scripts',
    'long_description': '# Executable Workflow\n\n[![PyPI](https://img.shields.io/pypi/v/py-executable-checklist?style=flat-square)](https://pypi.python.org/pypi/py-executable-checklist/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-executable-checklist?style=flat-square)](https://pypi.python.org/pypi/py-executable-checklist/)\n[![PyPI - License](https://img.shields.io/pypi/l/py-executable-checklist?style=flat-square)](https://pypi.python.org/pypi/py-executable-checklist/)\n\n\n---\n\n**Documentation**: [https://namuan.github.io/py-executable-checklist](https://namuan.github.io/py-executable-checklist)\n\n**Source Code**: [https://github.com/namuan/py-executable-checklist](https://github.com/namuan/py-executable-checklist)\n\n**PyPI**: [https://pypi.org/project/py-executable-checklist/](https://pypi.org/project/py-executable-checklist/)\n\n---\n\nHelper classes to develop executable workflow scripts\n\n## Installation\n\n```sh\npip install py-executable-checklist\n```\n\n## Example Usage\n\n```python\nimport logging\nfrom argparse import ArgumentParser, RawDescriptionHelpFormatter\n\nfrom py_executable_checklist.workflow import run_workflow, WorkflowBase\n\n\n# Common functions across steps\n\n# Workflow steps\n\nclass DoSomething(WorkflowBase):\n    """\n    Go to this page\n    Copy the command\n    Run the command\n    Copy the output and paste it into the email\n    """\n\n    username: str\n\n    def execute(self):\n        logging.info(f"Hello {self.username}")\n\n        # output\n        return {"greetings": f"Hello {self.username}"}\n\n\n# Workflow definition\n\n\ndef workflow():\n    return [\n        DoSomething,\n    ]\n\n\n# Boilerplate\n\n\ndef parse_args():\n    parser = ArgumentParser(\n        description=__doc__, formatter_class=RawDescriptionHelpFormatter\n    )\n    parser.add_argument("-u", "--username", type=str, required=True, help="User name")\n    parser.add_argument(\n        "-v",\n        "--verbose",\n        action="store_true",\n        default=False,\n        dest="verbose",\n        help="Display context variables at each step",\n    )\n    return parser.parse_args()\n\n\ndef main(args):\n    context = args.__dict__\n    run_workflow(context, workflow())\n\n\nif __name__ == "__main__":\n    args = parse_args()\n    main(args)\n```\n\n## Development\n\n* Clone this repository\n* Requirements:\n    * [Poetry](https://python-poetry.org/)\n    * Python 3.7+\n* Create a virtual environment and install the dependencies\n\n```sh\npoetry install\n```\n\n* Activate the virtual environment\n\n```sh\npoetry shell\n```\n\n### Validating build\n\n```sh\nmake build\n```\n\n### Release process\n\nA release is automatically published when a new version is bumped using `make bump`. See `.github/workflows/build.yml`\nfor more details. Once the release is published, `.github/workflows/publish.yml` will automatically publish it to PyPI.\n',
    'author': 'namuan',
    'author_email': 'github@deskriders.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://namuan.github.io/py-executable-checklist',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
