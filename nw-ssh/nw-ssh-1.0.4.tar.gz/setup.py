# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nw_ssh']

package_data = \
{'': ['*']}

install_requires = \
['asyncssh>=2.4.2,<3.0.0']

setup_kwargs = {
    'name': 'nw-ssh',
    'version': '1.0.4',
    'description': 'Simple ssh client with asyncssh for network devices',
    'long_description': "# nw-ssh\nSimple ssh client with asyncssh for network devices.\n\n```\nimport asyncio\nimport nw_ssh\n\nasync def main() -> None:\n    async with nw_ssh.SSHConnection(\n        host='169.254.0.1',\n        port=22,\n        username='root',\n        password='password',\n        client_keys=[],\n        passphrase=None,\n        known_hosts_file=None,\n        delimiter=r'#',\n        timeout=10,\n    ) as conn:\n\n        print(conn.login_message)\n\n        output = await conn.send(input='cli', delimiter=r'>')\n        print(output)\n\n        output = await conn.send(input='show interfaces fxp0 | no-more', delimiter=r'>')\n        print(output)\n\n        output = await conn.send(input='configure', delimiter=r'#')\n        print(output)\n\n        output = await conn.send(input='show interfaces', delimiter=r'#')\n        print(output)\n\n        output = await conn.send(input='commit', delimiter=r'#', timeout=10)\n        print(output)\n\nasyncio.run(main())\n```\n\n# Requirements\n- Python >= 3.7\n- asyncssh\n\n\n# Installation\n```\npip install nw-ssh\n```\n\n\n# License\nMIT\n",
    'author': 'dei',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kthrdei/nw-ssh',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
