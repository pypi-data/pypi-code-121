# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['lakai']

package_data = \
{'': ['*']}

install_requires = \
['dataclasses>=0.6,<0.7',
 'lark>=1.1.2,<2.0.0',
 'setuptools>=30.1.0',
 'typing-extensions>=3.0.0.0']

setup_kwargs = {
    'name': 'lakai',
    'version': '0.1.2',
    'description': '',
    'long_description': '# lakai\n\nLakai is a wrapper around [Lark][] that provides a convenient API.\n\n  [Lark]: https://github.com/lark-parser/lark\n\n## Installation\n\n    $ pip install lakai\n\n## Usage\n\n```py\nimport lakai\ngrammar = r"""\n    %ignore /\\s+/\n    %import common.INT\n    ?atom: INT\n    ?!product: atom | product "*" atom | product "/" atom\n    ?!sum: product | sum "+" product | sum "-" product\n"""\nparser = lakai.from_string(grammar, start="sum")\ntree = parser.parse("1 + 3 * 2 + 4 / 2")\nlakai.pprint(tree)\n```\n\nGives\n\n```\nsum\n    sum\n        INT: \'1\'\n        PLUS: \'+\'\n        product\n            INT: \'3\'\n            STAR: \'*\'\n            INT: \'2\'\n    PLUS: \'+\'\n    product\n        INT: \'4\'\n        SLASH: \'/\'\n        INT: \'2\'\n```\n\nTo evaluate the expression, you can use a `lakai.Transformer`:\n\n```py\nimport operator\n\nclass Computer(lakai.Transformer):\n    operators = {"/": operator.truediv, "*": operator.mul, "-": operator.sub, "+": operator.add}\n\n    def visit_INT(self, leaf: lakai.Leaf) -> int:\n        return int(leaf.value)\n\n    def visit_product(self, node: lakai.Node[Any]) -> int:\n        return self.operators[node.children[1].value](node.children[0], node.children[2])\n\n    visit_sum = visit_product\n\nassert Computer().visit(tree) == 9\n```\n\n\nTo use Lakai with a Lark standalone parser:\n\n```py\nimport lakai\nfrom ._standalone import Lark_Standalone\nparser = lakai.Lakai(Lark_Standalone())\n```\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
