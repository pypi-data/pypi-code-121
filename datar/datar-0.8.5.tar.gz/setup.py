# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datar',
 'datar.base',
 'datar.core',
 'datar.core.backends',
 'datar.core.backends.pandas',
 'datar.core.backends.pandas.api',
 'datar.core.backends.pandas.core',
 'datar.datar',
 'datar.datasets',
 'datar.dplyr',
 'datar.forcats',
 'datar.tibble',
 'datar.tidyr']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.3,<2.0', 'pipda>=0.6,<0.7', 'python-simpleconf[toml]>=0.5,<0.6']

extras_require = \
{'modin': ['modin>=0.10,<0.11'],
 'pdtypes': ['pdtypes>=0.0,<0.1'],
 'scipy': ['scipy>=1.6,<2.0'],
 'slugify': ['python-slugify>=6,<7'],
 'wcwidth': ['wcwidth>=0.2,<0.3']}

setup_kwargs = {
    'name': 'datar',
    'version': '0.8.5',
    'description': 'Port of dplyr and other related R packages in python, using pipda.',
    'long_description': '# datar\n\nA Grammar of Data Manipulation in python\n\n<!-- badges -->\n[![Pypi][6]][7] [![Github][8]][9] ![Building][10] [![Docs and API][11]][5] [![Codacy][12]][13] [![Codacy coverage][14]][13]\n\n[Documentation][5] | [Reference Maps][15] | [Notebook Examples][16] | [API][17] | [Blog][18]\n\n<img width="30%" style="margin: 10px 10px 10px 30px" align="right" src="logo.png">\n\n`datar` is a re-imagining of APIs of data manipulation libraries in python (currently only `pandas` supported) so that you can manipulate your data with it like with `dplyr` in `R`.\n\n`datar` is an in-depth port of `tidyverse` packages, such as `dplyr`, `tidyr`, `forcats` and `tibble`, as well as some functions from base R.\n\n## Installation\n\n```shell\npip install -U datar\n\n# install pdtypes support\npip install -U datar[pdtypes]\n\n# install dependencies for modin as backend\npip install -U datar[modin]\n# you may also need to install dependencies for modin engines\n# pip install -U modin[ray]\n```\n\n## Example usage\n\n```python\nfrom datar import f\nfrom datar.dplyr import mutate, filter, if_else\nfrom datar.tibble import tibble\n# or\n# from datar.all import f, mutate, filter, if_else, tibble\n\ndf = tibble(\n    x=range(4),  # or f[:4]\n    y=[\'zero\', \'one\', \'two\', \'three\']\n)\ndf >> mutate(z=f.x)\n"""# output\n        x        y       z\n  <int64> <object> <int64>\n0       0     zero       0\n1       1      one       1\n2       2      two       2\n3       3    three       3\n"""\n\ndf >> mutate(z=if_else(f.x>1, 1, 0))\n"""# output:\n        x        y       z\n  <int64> <object> <int64>\n0       0     zero       0\n1       1      one       0\n2       2      two       1\n3       3    three       1\n"""\n\ndf >> filter(f.x>1)\n"""# output:\n        x        y\n  <int64> <object>\n0       2      two\n1       3    three\n"""\n\ndf >> mutate(z=if_else(f.x>1, 1, 0)) >> filter(f.z==1)\n"""# output:\n        x        y       z\n  <int64> <object> <int64>\n0       2      two       1\n1       3    three       1\n"""\n```\n\n```python\n# works with plotnine\n# example grabbed from https://github.com/has2k1/plydata\nimport numpy\nfrom datar.base import sin, pi\nfrom plotnine import ggplot, aes, geom_line, theme_classic\n\ndf = tibble(x=numpy.linspace(0, 2*pi, 500))\n(df >>\n  mutate(y=sin(f.x), sign=if_else(f.y>=0, "positive", "negative")) >>\n  ggplot(aes(x=\'x\', y=\'y\')) +\n  theme_classic() +\n  geom_line(aes(color=\'sign\'), size=1.2))\n```\n\n![example](./example.png)\n\n```python\n# easy to integrate with other libraries\n# for example: klib\nimport klib\nfrom datar.core.factory import verb_factory\nfrom datar.datasets import iris\nfrom datar.dplyr import pull\n\ndist_plot = verb_factory(func=klib.dist_plot)\niris >> pull(f.Sepal_Length) >> dist_plot()\n```\n\n![example](./example2.png)\n\nSee also some advanced examples from my answers on StackOverflow:\n\n- [Compare 2 DataFrames and drop rows that do not contain corresponding ID variables](https://stackoverflow.com/a/71532167/5088165)\n- [count by id with dynamic criteria](https://stackoverflow.com/a/71519157/5088165)\n- [counting the frequency in python size vs count](https://stackoverflow.com/a/71516503/5088165)\n- [Pandas equivalent of R/dplyr group_by summarise concatenation](https://stackoverflow.com/a/71490832/5088165)\n- [ntiles over columns in python using R\'s "mutate(across(cols = ..."](https://stackoverflow.com/a/71490501/5088165)\n- [Replicate R Solution in Python for Calculating Monthly CRR](https://stackoverflow.com/a/71490194/5088165)\n- [Best/Concise Way to Conditionally Concat two Columns in Pandas DataFrame](https://stackoverflow.com/a/71443587/5088165)\n- [how to transform R dataframe to rows of indicator values](https://stackoverflow.com/a/71443515/5088165)\n- [Left join on multiple columns](https://stackoverflow.com/a/71443441/5088165)\n- [Python: change column of strings with None to 0/1](https://stackoverflow.com/a/71429016/5088165)\n- [Comparing 2 data frames and finding values are not in 2nd data frame](https://stackoverflow.com/a/71415818/5088165)\n- [How to compare two Pandas DataFrames based on specific columns in Python?](https://stackoverflow.com/a/71413499/5088165)\n- [expand.grid equivalent to get pandas data frame for prediction in Python](https://stackoverflow.com/a/71376414/5088165)\n- [Python pandas equivalent to R\'s group_by, mutate, and ifelse](https://stackoverflow.com/a/70387267/5088165)\n- [How to convert a list of dictionaries to a Pandas Dataframe with one of the values as column name?](https://stackoverflow.com/a/69094005/5088165)\n- [Moving window on a Standard Deviation & Mean calculation](https://stackoverflow.com/a/69093067/5088165)\n- [Python: creating new "interpolated" rows based on a specific field in Pandas](https://stackoverflow.com/a/69092696/5088165)\n- [How would I extend a Pandas DataFrame such as this?](https://stackoverflow.com/a/69092067/5088165)\n- [How to define new variable based on multiple conditions in Pandas - dplyr case_when equivalent](https://stackoverflow.com/a/69080870/5088165)\n- [What is the Pandas equivalent of top_n() in dplyr?](https://stackoverflow.com/a/69080806/5088165)\n- [Equivalent of fct_lump in pandas](https://stackoverflow.com/a/69080727/5088165)\n- [pandas equivalent of fct_reorder](https://stackoverflow.com/a/69080638/5088165)\n- [Is there a way to find out the 2 X 2 contingency table consisting of the count of values by applying a condition from two dataframe](https://stackoverflow.com/a/68674345/5088165)\n- [Count if array in pandas](https://stackoverflow.com/a/68659334/5088165)\n- [How to create a new column for transposed data](https://stackoverflow.com/a/68642891/5088165)\n- [How to create new DataFrame based on conditions from another DataFrame](https://stackoverflow.com/a/68640494/5088165)\n- [Refer to column of a data frame that is being defined](https://stackoverflow.com/a/68308077/5088165)\n- [How to use regex in mutate dplython to add new column](https://stackoverflow.com/a/68308033/5088165)\n- [Multiplying a row by the previous row (with a certain name) in Pandas](https://stackoverflow.com/a/68137136/5088165)\n- [Create dataframe from rows under a row with a certain condition](https://stackoverflow.com/a/68137089/5088165)\n- [pandas data frame, group by multiple cols and put other columns\' contents in one](https://stackoverflow.com/a/68136982/5088165)\n- [Pandas custom aggregate function with condition on group, is it possible?](https://stackoverflow.com/a/68136704/5088165)\n- [multiply different values to pandas column with combination of other columns](https://stackoverflow.com/a/68136300/5088165)\n- [Vectorized column-wise regex matching in pandas](https://stackoverflow.com/a/68124082/5088165)\n- [Iterate through and conditionally append string values in a Pandas dataframe](https://stackoverflow.com/a/68123912/5088165)\n- [Groupby mutate equivalent in pandas/python using tidydata principles](https://stackoverflow.com/a/68123753/5088165)\n- [More ...](https://stackoverflow.com/search?q=user%3A5088165+and+%5Bpandas%5D)\n\n\n[1]: https://tidyr.tidyverse.org/index.html\n[2]: https://dplyr.tidyverse.org/index.html\n[3]: https://github.com/pwwang/pipda\n[4]: https://tibble.tidyverse.org/index.html\n[5]: https://pwwang.github.io/datar/\n[6]: https://img.shields.io/pypi/v/datar?style=flat-square\n[7]: https://pypi.org/project/datar/\n[8]: https://img.shields.io/github/v/tag/pwwang/datar?style=flat-square\n[9]: https://github.com/pwwang/datar\n[10]: https://img.shields.io/github/workflow/status/pwwang/datar/Build%20and%20Deploy?style=flat-square\n[11]: https://img.shields.io/github/workflow/status/pwwang/datar/Build%20Docs?label=Docs&style=flat-square\n[12]: https://img.shields.io/codacy/grade/3d9bdff4d7a34bdfb9cd9e254184cb35?style=flat-square\n[13]: https://app.codacy.com/gh/pwwang/datar\n[14]: https://img.shields.io/codacy/coverage/3d9bdff4d7a34bdfb9cd9e254184cb35?style=flat-square\n[15]: https://pwwang.github.io/datar/reference-maps/ALL/\n[16]: https://pwwang.github.io/datar/notebooks/across/\n[17]: https://pwwang.github.io/datar/api/datar/\n[18]: https://pwwang.github.io/datar-blog\n[19]: https://github.com/pwwang/datar-cli\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pwwang/datar',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
