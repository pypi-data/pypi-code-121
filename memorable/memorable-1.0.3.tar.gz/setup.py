# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['memorable']

package_data = \
{'': ['*'], 'memorable': ['_resources/*', '_resources/nouns/*']}

setup_kwargs = {
    'name': 'memorable',
    'version': '1.0.3',
    'description': 'A library for creating memorable strings.',
    'long_description': "# Memorable\n\nA library for generating memorable strings.\n\n## Usage\n\n```python\nimport memorable\n\nmemorable.name()\n# lue-the-jealously-happy-go-lucky\nmemorable.action()\n# eat-a-pretty-payment\nmemorable.thing()\n# cleverly-neglected-talk\nmemorable.code_phrase()\n# amused-chilly-minestrone-distribute\n```\n\n## Advanced usage\n\nIt is possible to generate strings focusing on a specific theme.\n\n```python\nfor kind in memorable.NounTypes:\n    phrase = memorable.thing(kind=kind)\n    print(f'{kind.value}: {phrase}')\n    # alcohols: wonderfully-overdue-beer\n    # animals: uncritically-thoughtful-octopus\n    # elements: vividly-mindless-chromium\n    # foods: jubilantly-snappy-stew\n    # fruits: poorly-handmade-kiwano\n    # geographies: quaintly-mountainous-beach\n    # households: hurriedly-ready-zester\n    # investments: meticulously-variable-bitcoin\n    # literature: madly-bogus-ode\n    # mythical: readily-general-centaur\n    # occupations: casually-tinted-data-scientist\n    # organs: nightly-splendid-lungs\n    # places: casually-definitive-farm\n    # relations: later-ready-babushka\n    # rocks: slavishly-hot-picrite\n    # royalty: fast-loyal-despot\n    # tools: unnecessarily-unripe-needle-nose\n    # transports: hollowly-cheerful-pickup\n    # trees: never-offbeat-fir\n    # vegtables: naively-happy-bitter-melon\n    # water_bodies: upliftingly-flickering-wadi\n```\n\nIf `memorable` is being used to generate ids and you'd like to reduce the\nfrequency of collisions (you should expect some collisions) it's possible\nto request some extra characters tacked on the end to make them less common.\n\n```python\nmemorable.action(extra_characters=4)\n# demand-the-hidden-bread-machine-gths\n```",
    'author': 'Kevin Schiroo',
    'author_email': 'kjschiroo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/kjschiroo/memorable',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
