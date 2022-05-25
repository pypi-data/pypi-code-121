# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kripta_py']

package_data = \
{'': ['*']}

install_requires = \
['pycryptodome>=3.14.1,<4']

setup_kwargs = {
    'name': 'kripta-py',
    'version': '0.1.1',
    'description': 'A tiny asymmetric/symmetric ecnryption lib for humans.',
    'long_description': '# kripta-py\n\nAn simple implementation of a Symmetric(AES) and Asymmetric(RSA) encryption based on [pycryptodome](https://github.com/Legrandin/pycryptodome) module.\n\n## Requirements\n\n- Python (3.10 recommended)\n\n## Features\n\n- Generate RSA keys like\n- Encrypt/Decrypt messages, files, binaries on symmetric or asymmetric\n\n## How to use\n\n- Install the lib\n```bash\npip install kripta-py\n```\n\n- To use the **symmetric encryption** (AES):\n    - Schema :\n        <img\n            src="https://github.com/Sanix-Darker/kripta/raw/master/images/s.png"\n            alt="drawing"\n            width="400"\n        />\n    - Code :\n        ```python\n        from kripta_py import KriptaAES\n\n\n        message = "secret-message"\n        secret_key = "secret-code-password"\n\n        k = KriptaAES()\n        # to encrypt\n        encrypted_msg = k.encrypt(message, secret_key)\n\n        # to decrypt\n        print(k.decrypt(encrypted_msg1, secret_key).decode())\n        # secret-message \n        ```\n\n- To use an **asymmetric encryption** (RSA):\n    - Schema :\n        <img\n            src="https://github.com/Sanix-Darker/kripta/raw/master/images/as.gif"\n            alt="drawing"\n            width="400"\n        />\n    - Code example:\n        ```python\n        from kripta_py import KriptaRSA\n\n\n        message = "secret-message"\n        pub_key = """-----BEGIN PUBLIC KEY-----\n        ....\n        -----END PUBLIC KEY-----"""\n\n        k = KriptaRSA()\n        k.setPublicKey(pub_key)\n        # To encrypt a message\n        encrypted_msg = k.encrypt(k.getPublicKey(), message.encode())\n\n        priv_key = """-----BEGIN RSA PRIVATE KEY-----\n        .....\n        -----END RSA PRIVATE KEY-----"""\n\n        k.setPrivateKey(priv_key)\n        # To decrypt\n        print(k.decrypt(encrypted_msg).decode())\n        # secret-message \n        ```\n',
    'author': 'sanix-darker',
    'author_email': 's4nixd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
