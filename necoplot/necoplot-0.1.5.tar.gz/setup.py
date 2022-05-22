# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['necoplot']

package_data = \
{'': ['*']}

install_requires = \
['japanize-matplotlib>=1.1.3,<2.0.0', 'matplotlib>=3.5.1,<4.0.0']

setup_kwargs = {
    'name': 'necoplot',
    'version': '0.1.5',
    'description': 'A matplotlib wrapper; It may help you to write plotting code briefly.',
    'long_description': "# necoplot\n`necoplot` is a matplotlib wrapper.  \nIt may help you to write plotting code briefly.\n\n\n## Installation\n`pip install necoplot`\n\n\n## Usage examples\n\n```python\nimport necoplot as neco\n\nimport numpy as np\n\nxx = np.linspace(-5,5,20)\nyy = xx*xx\n\n# Basic\nwith neco.plot() as ax:\n    ax.plot(xx, yy)\n```\n![example01_basic](https://user-images.githubusercontent.com/104950574/167246388-d9b5fe6b-dd30-4609-9ded-e96fa6016959.jpeg)\n\n\n```python\n# Config figiure\nwith neco.plot(figsize=(4,4), dpi=80, facecolor='silver') as ax:\n    ax.plot(xx, yy)\n```\n![example02_config_figure](https://user-images.githubusercontent.com/104950574/167246391-5f91a775-a8d6-48b6-bfee-7304efe7076f.jpeg)\n\n\n```python\n# Config ax by plot() \nwith neco.plot(figsize=(6,4), xlim=(-5,0)) as ax:\n    ax.plot(xx, yy) \n```\n![example03_config_by_plot](https://user-images.githubusercontent.com/104950574/167246392-efc17842-a9ad-4fe9-9823-a3ce0c32281a.jpeg)\n\n\n```python\n# Config ax by using config_ax()\nax0 = neco.config_ax(xlim=(1,5), title='title', xscale='log')\n\nwith neco.plot(ax0, figsize=(6,4)) as ax:\n    ax.plot(xx, yy)\n```\n![example04_config_ax](https://user-images.githubusercontent.com/104950574/167246394-13d89094-f43f-4d66-8adf-f8b59a3fb4ca.jpeg)\n\n\n```python\n# Config ax directry\nwith neco.plot() as ax:\n    ax.plot(xx, yy, label='x squared')\n    ax.legend()\n    ax.hlines(y=25, xmin=-5, xmax=5)\n```\n![example05_config_directry](https://user-images.githubusercontent.com/104950574/167246396-d5fefe64-1db5-4252-8ab0-1d119f77a113.jpeg)\n\n```python\n# Save figure\nwith neco.plot() as ax:\n    ax.plot(xx, yy)\n    neco.save('sample.png', show=False)\n```\n\n```python\n# Plot multiple with mplot()\nax0 = neco.config_ax(121, xlim=(-5, 0),title='Left side')\nax1 = neco.config_ax(122, xlim=(0, 5), title='Right side', yticks=[])\n\nwith neco.mplot([ax0, ax1]) as p:\n    p.axes[0].plot(xx, yy)\n    p.axes[1].plot(xx, yy)\n```\n![exmaple08](https://user-images.githubusercontent.com/104950574/167278508-0a7483d3-08f7-495f-9c02-9a689a546dde.jpeg)\n\n```python\n# Config default values\nneco.config_user_parameters(title='New default title!')\n\nwith neco.plot() as ax:\n    ax.plot(xx, yy)\n```\n![example07_config_params](https://user-images.githubusercontent.com/104950574/167246398-33484f92-f70b-4629-b8cd-86854ed1a2c3.jpeg)\n\n\n```python\n# Reset config\nneco.reset()\n\n```\n\n## Adovanced\n### Slope chart\n\n```python\n# Make a simple slope chart\nnames = ['Apple', 'Banana', 'Cheese', 'Donut', 'Egg']\ntime0 = [10, 8, 7, 5, 4]\ntime1 = [8, 11, 4, 2, 3]\n\nwith neco.slope() as slope:\n    slope.plot(time0, time1, names)\n```\n![simple_slope](https://user-images.githubusercontent.com/104950574/169690698-fb64f95f-8388-4c88-914e-60089082c856.jpeg)\n\n\n```python\n# Make another chart which a little more complicated\ntitle = 'Example of a slope chart'\nsubtitle = 'Food names | Some numbers'\n\nwith neco.slope(figsize=(4, 5)) as slope:\n    slope.highlight({'Banana':'orange'})\n    slope.config(xstart=0.2, xend=0.9, suffix='%')\n    slope.plot(time0, time1, names, xticks=('Time0', 'Time1'), \n               title=title, subtitle=subtitle)\n```\n![custmized_slope](https://user-images.githubusercontent.com/104950574/169690693-525e79c9-b955-4fa9-a6a8-0cb7e8aa6a1b.jpeg)\n",
    'author': 'guneco',
    'author_email': 'gu3fav@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/guneco',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
