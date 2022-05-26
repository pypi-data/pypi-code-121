# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gitlab_evaluate',
 'gitlab_evaluate.ci_readiness',
 'gitlab_evaluate.lib',
 'gitlab_evaluate.migration_readiness',
 'gitlab_evaluate.models']

package_data = \
{'': ['*'], 'gitlab_evaluate': ['data/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'gitlab-ps-utils>=0.5.0,<0.6.0',
 'pydantic>=1.8.2,<2.0.0',
 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['evaluate-ci-readiness = gitlab_evaluate.evaluate_ci:main',
                     'evaluate-gitlab = gitlab_evaluate.main:main']}

setup_kwargs = {
    'name': 'gitlab-evaluate',
    'version': '0.5.1',
    'description': 'Scans GitLab instance and ranks projects against a set of criteria. Can be used to identiy projects that may have too much metadata/size to reliably export or import.',
    'long_description': "# Evaluate\nEvaluate is a script that can be run to gather information about projects from a gitlab self-managed instance. This information is useful to the GitLab Professional Services (PS) team to accurately scope migration services. \n\n## Use Case\nGitLab PS plans to share this script with a Customer to run against their self managed instance. Then the customer can send back the output files to enable GitLab engagement managers to scope engagements accurately. \n\n## Install\n\n```\npip install gitlab-evaluate\n```\n\n## Usage\n\n### System level data gathering\nEvaluate is meant to be run by an administrator of a GitLab Self Managed deployment to gather data about every project on the instance. \n\n1. A GitLab system administrator should  [provision an access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#create-a-personal-access-token)\n1. Then, after installing `gitlab-evaluate` from the [Install](#install) section above,\n1. Run :point_down: \n\n```bash\n# For evaluating a GitLab instance\nevaluate-gitlab -t <access-token-with-api-admin-privileges> -s https://gitlab.example.com\n```\n1. This should create a file called `evaluate_output.csv`\n1. If you're coordinating a GitLab Professional Services engageemnt, email this file to the GitLab account team. \n\n### To gather CI data from a single repo\n\n```bash\n# For evaluating a single git repo's CI readiness\nevaluate-ci-readiness -r|--repo <git-repo-url>\n```\n\n### Command help screen\n\n```\nusage: evaluate-gitlab [-h] [-t TOKEN] [-s SOURCE] [-f FILENAME] [-o] [-i] [-p PROCESSES]\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -t TOKEN, --token TOKEN\n                        Personal Access Token: REQ'd\n  -s SOURCE, --source SOURCE\n                        Source URL: REQ'd\n  -f FILENAME, --filename FILENAME\n                        CSV Output File Name. If not set, will default to 'evaluate_output.csv'\n  -o, --output          Output Per Project Stats to screen\n  -i, --insecure        Set to ignore SSL warnings.\n  -p PROCESSES, --processes PROCESSES\n                        Number of processes. Defaults to number of CPU cores\n```\n\n```\nusage: evaluate-ci-readiness [-h] [-r REPO]\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -r REPO, --repo REPO  Git Repository To Clone (ex: https://username:password@repo.com\n```\n\n## Using a docker container\n\n[Docker containers with evaluate installed](https://gitlab.com/gitlab-org/professional-services-automation/tools/utilities/evaluate/container_registry) are also available to use.\n\n### Local usage\n\n```bash\n# Spin up container\ndocker run --name evaluate -it registry.gitlab.com/gitlab-org/professional-services-automation/tools/utilities/evaluate:latest /bin/bash\n\n# In docker shell\nevaluate-ci-readiness -r|--repo <git-repo-url>\nevaluate-gitlab -t <access-token-with-api-admin-privileges> -s https://gitlab.example.com\n```\n\n### Example GitLab CI job using evaluate ci readiness script\n\n```yaml\nevaluate node-js:\n  stage: test\n  script:\n    - evaluate-ci-readiness --repo=https://github.com/nodejs/node.git\n  artifacts:\n    paths:\n      - node.csv\n```\n\nTo **test**, consider standing up local docker container of gitlab. Provision a personal access token of a user who has system admin priviledges. Create multiple projects with varying number of commits, pipelines, merge requests, issues. Consider importing an open source repo or using [GPT](https://gitlab.com/gitlab-org/quality/performance) to add projects to the system.  \n\n## Design\nDesign for the script can be found [here](https://gitlab.com/gitlab-com/customer-success/professional-services-group/ps-leadership-team/ps-practice-management/-/issues/83)\n\n## Project Thresholds\n_Below are the thresholds we will use to determine whether a project can be considered for normal migration or needs to have special steps taken in order to migrate_ \n\n### Project Data\n- Pipelines - 1,500 max\n- Issues - 1,500 total (not just open)\n- Merge Requests - 1,500 total (not just merged)\n- Container images - 20GB per project\n- Packages - Any packages present\n\n### Repo Data\n- commits - 20K\n- branches - 1K\n- tags - 1K\n- Disk Size - 10GB\n",
    'author': 'GitLab Professional Services',
    'author_email': 'proserv@gitlab.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/gitlab-org/professional-services-automation/tools/utilities/evaluate',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0',
}


setup(**setup_kwargs)
