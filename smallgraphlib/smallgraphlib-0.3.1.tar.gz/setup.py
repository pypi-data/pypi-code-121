# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['smallgraphlib']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'smallgraphlib',
    'version': '0.3.1',
    'description': 'Simple library for handling small graphs, including Tikz code generation.',
    'long_description': '# Small Graph Lib\n\n## Installing\n\n    $ git clone https://github.com/wxgeo/smallgraphlib\n\n    $ pip install --user smallgraphlib\n\n## Usage\n\nMain classes are `Graph`, `DirectedGraph`, `WeightedGraph` and `WeightedDirectedGraph`:\n\n    >>> from smallgraphlib import DirectedGraph\n    >>> g = DirectedGraph(["A", "B", "C"], ("A", "B"), ("B", "A"), ("B", "C"))\n    >>> g.is_simple\n    True\n    >>> g.is_complete\n    False\n    >>> g.is_directed\n    True\n    >>> g.adjacency_matrix\n    [[0, 1, 0], [1, 0, 1], [0, 0, 0]]\n    >>> g.degree\n    3\n    >>> g.order\n    3\n    >>> g.is_eulerian\n    False\n    >>> g.is_semi_eulerian\n    True\n\nSpecial graphs may be generated using factory functions:\n    \n    >>> from smallgraphlib import complete_graph, complete_bipartite_graph\n    >>> K5 = complete_graph(5)\n    >>> len(K5.greedy_coloring)\n    5\n    >>> K33 = complete_bipartite_graph(3, 3)\n    >>> K33.degree\n    6\n    >>> K33.diameter\n    2\n    \nIf the graph is not to complex, Tikz code may be generated:\n\n    >>> g.as_tikz()\n    ...\n\n## Development\n\n1. Get last version:\n   \n       $ git clone https://github.com/wxgeo/smallgraphlib\n\n2. Install Poetry.\n    \n   Poetry is a tool for dependency management and packaging in Python.\n\n   Installation instructions are here:\n   https://python-poetry.org/docs/#installation\n\n3. Install developments tools:\n    \n       $ poetry install\n\n4. Optionally, update development tools:\n      \n       $ poetry update\n\n5. Optionally, install library in editable mode:\n\n       $ pip install -e smallgraphlib\n\n6. Make changes, add tests.\n  \n7. Launch tests:\n\n        $ tox\n\n8. Everything\'s OK ? Commit. :)',
    'author': 'Nicolas Pourcelot',
    'author_email': 'nicolas.pourcelot@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wxgeo/smallgraphlib',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
