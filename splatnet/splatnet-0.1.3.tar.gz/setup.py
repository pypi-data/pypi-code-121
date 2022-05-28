# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['splatnet', 'splatnet.splatnet2']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.11.1,<5.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'splatnet',
    'version': '0.1.3',
    'description': 'Wrapper for Splatnet (Splatoon API)',
    'long_description': '# splatnet\n\nPython wrapper for Splatnet API (Splatoon API).\n\n## Install\n\n```bash\npip install splatnet\n```\n\n## Usage\n\n```python\nfrom splatnet.splatnet2 import Config, Splatnet2\n\nconfig = Config()\nsplatnet = Splatnet2(config)\n\nresults = splatnet.results()\n\ntotal_paint_point = 0\nteam_total_kill_count = 0\n\nfor r in results.results:\n    total_paint_point += r.player_result.game_paint_point\n\n    # Get all data of a battle\n    result = splatnet.result(r.battle_number)\n\n    for player_result in result.my_team_members:\n        team_total_kill_count += player_result.kill_count\n\n    team_total_kill_count += result.player_result.kill_count\n\nprint(f"{total_paint_point=}")\nprint(f"{team_total_kill_count=}")\n```\n\n## Data Schema\n\nSee [schema definition](https://github.com/unatoon/splatnet/blob/main/splatnet/splatnet2/models.py).\n\n## Config\n\nYou can specify config file path and language.\n\n```python\nfrom splatnet.splatnet2 import Config\n\nconfig = Config(path="path/to/config.json", language="ja-JP")\n```',
    'author': 'unatoon',
    'author_email': 'unatoon@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/unatoon/splatnet',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
