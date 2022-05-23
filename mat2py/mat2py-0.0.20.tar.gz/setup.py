# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mat2py',
 'mat2py.common',
 'mat2py.core',
 'mat2py.core._internal',
 'mat2py.toolbox.matlab.elmat',
 'mat2py.toolbox.matlab.polyfun',
 'mat2py.toolbox.signal.signal']

package_data = \
{'': ['*']}

install_requires = \
['executing>=0.8.3,<0.9.0', 'numpy>=1.21.4,<2.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=4.5.0,<5.0.0',
                             'scipy>=1.7,<1.8'],
 ':python_version >= "3.8"': ['scipy>=1.7.0,<2.0.0']}

setup_kwargs = {
    'name': 'mat2py',
    'version': '0.0.20',
    'description': 'mat2py mean to be drop-in replacement of Matlab by wrapping Numpy/Scipy/... packages.',
    'long_description': '# mat2py\n\n<div align="center">\n\n[![Build status](https://github.com/mat2py/mat2py/workflows/build/badge.svg?branch=master&event=push)](https://github.com/mat2py/mat2py/actions?query=workflow%3Abuild)\n[![Python Version](https://img.shields.io/pypi/pyversions/mat2py.svg)](https://pypi.org/project/mat2py/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/mat2py/mat2py/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/mat2py/mat2py/blob/master/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/mat2py/mat2py/releases)\n[![License](https://img.shields.io/github/license/mat2py/mat2py)](https://github.com/mat2py/mat2py/blob/master/LICENSE)\n![Coverage Report](assets/images/coverage.svg)\n\nmat2py mean to be drop-in replacement of Matlab by wrapping Numpy/Scipy/... packages.\n\n</div>\n\nFor instance usage, try the *Online Matlab Emulator* [here](https://console.mat2py.org/). \nPlease note:\n- You may need the latest modern browser for using this APP(check the console log by pressing F12).\n- Loading the environment may take quite long time, especially for the first time. Try refresh the page incase bad network connection.\n- Do a feature request when encounter `NotImplementedError`.\n\n![Coverage Report](assets/images/console.png)\n\nTry copy-paste following code to the emulator and feel its capability:\n\n```matlab\nxv = [0.5;0.2;1.0;0;0.8;0.5];\nyv = [1.0;0.1;0.7;0.7;0.1;1];\nxq = [0.1;0.5;0.9;0.2;0.4;0.5;0.5;0.9;0.6;0.8;0.7;0.2];\nyq = [0.4;0.6;0.9;0.7;0.3;0.8;0.2;0.4;0.4;0.6;0.2;0.6];\n\n[in,on] = inpolygon(xq,yq,xv,yv);\n\nplot(xv,yv, ... % polygon\n     xq(in&~on),yq(in&~on),\'r+\', ...  % points strictly inside\n     xq(on),yq(on),\'k*\', ... % points on edge\n     xq(~in),yq(~in),\'bo\' ... % points outside\n)\n```\n\nThe final goal of this APP is to create a **serverless**, **Matlab compatiable** console completely in end-users\' browser.\n\n## First Steps\n\n### Installation\n\n```bash\npython3 -m pip install -U mat2py\n```\n\nor install with `Poetry`\n\n```bash\npoetry add mat2py\n```\n\n### Install the translator `mh_python` if needed\n```bash\npython3 -m pip install -U mh-python\n```\n\n### Try the example `demo_fft`\n\n```bash\n# download the one already converted and formatted\nwget https://raw.githubusercontent.com/mat2py/mat2py/main/tests/test_example/demo_fft.py\n\n# or convert it yourself\necho "wget https://raw.githubusercontent.com/mat2py/miss_hit/matlab2numpy/tests/mat2np/demo_fft.m"\necho "mh_python --python-alongside --format demo_fft.m"\n\n# run it...\npython3 demo_fft.py\n```\n\nYou can also **try out** the [online translator](https://translate.mat2py.org/) by modifiy the example or put your own code.\n\n## For Developer\n\n### Initialize your code\n\n1. Clone `mat2py`:\n\n```bash\ngit clone https://github.com/mat2py/mat2py \n```\n\n2. If you don\'t have `Poetry` installed run:\n\n```bash\nmake poetry-download\nsource ~/.poetry/env\n```\n\n3. Initialize poetry and install `pre-commit` hooks:\n\n```bash\nmake install\nmake pre-commit-install\n```\n\n4. Run the lint to check:\n\n```bash\nmake lint\n```\n\n## ToDO\n\n- A serverless web service for run `.m`/`.py` code inside browser\n- Complete set of [MATLAB® Basic Functions](https://www.mathworks.com/content/dam/mathworks/fact-sheet/matlab-basic-functions-reference.pdf)\n- Copy-on-Write beheviour\n- A cleaner class hierarchy\n- Enable `lint`(mypy, UT, etc.)\n\n## 📈 Releases\n\nYou can see the list of available releases on the [GitHub Releases](https://github.com/mat2py/mat2py/releases) page.\n\nWe follow [Semantic Versions](https://semver.org/) specification.\n\nWe use [`Release Drafter`](https://github.com/marketplace/actions/release-drafter). As pull requests are merged, a draft release is kept up-to-date listing the changes, ready to publish when you’re ready. With the categories option, you can categorize pull requests in release notes using labels.\n\n## 🛡 License\n\n[![License](https://img.shields.io/github/license/mat2py/mat2py)](https://github.com/mat2py/mat2py/blob/master/LICENSE)\n\nThis project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/mat2py/mat2py/blob/master/LICENSE) for more details.\n\n## 📃 Citation\n\n```bibtex\n@misc{mat2py,\n  author = {mat2py},\n  title = {mat2py mean to be drop-in replacement of Matlab by wrapping Numpy/Scipy/... packages.},\n  year = {2021},\n  publisher = {GitHub},\n  journal = {GitHub repository},\n  howpublished = {\\url{https://github.com/mat2py/mat2py}}\n}\n```\n\n## Credits [![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)\n\n- This project was initially generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)\n- The Matlab to Python translator `mh_python` is developed under fork of [MISS HIT](https://github.com/florianschanda/miss_hit), a fantastic Matlab static analysis tool.\n- The [serverless console](https://console.mat2py.org/) is created based on [Pyodide](https://pyodide.org/).\n',
    'author': 'mat2py',
    'author_email': 'chaoqingwang.nick@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://mat2py.org',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
